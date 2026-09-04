const express = require('express');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3002;

// Services
const late = require('./services/late');
const supabase = require('./services/supabase');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Explicit root route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Storage mode detection
const useSupabase = supabase.isConfigured();
console.log(`Storage mode: ${useSupabase ? 'Supabase (persistent)' : 'File (ephemeral - configure SUPABASE_URL and SUPABASE_ANON_KEY for persistence)'}`);

// ============================================
// File-based fallback (for local dev only)
// ============================================
const POSTS_FILE = path.join(__dirname, 'data', 'posts.json');

if (!fs.existsSync(path.join(__dirname, 'data'))) {
  fs.mkdirSync(path.join(__dirname, 'data'), { recursive: true });
}

function loadPostsFromFile() {
  if (!fs.existsSync(POSTS_FILE)) {
    return { posts: [] };
  }
  return JSON.parse(fs.readFileSync(POSTS_FILE, 'utf8'));
}

function savePostsToFile(data) {
  fs.writeFileSync(POSTS_FILE, JSON.stringify(data, null, 2));
}

// ============================================
// Unified Storage API
// ============================================

async function getAllPosts(filters = {}) {
  if (useSupabase) {
    return await supabase.getPosts(filters);
  } else {
    let posts = loadPostsFromFile().posts;
    if (filters.status) {
      posts = posts.filter(p => p.status === filters.status);
    }
    posts.sort((a, b) => new Date(b.created_at || b.createdAt) - new Date(a.created_at || a.createdAt));
    return posts;
  }
}

async function getPostById(id) {
  if (useSupabase) {
    return await supabase.getPost(id);
  } else {
    const data = loadPostsFromFile();
    return data.posts.find(p => p.id === id);
  }
}

async function createNewPost(post) {
  if (useSupabase) {
    return await supabase.createPost(post);
  } else {
    const data = loadPostsFromFile();
    data.posts.unshift(post);
    savePostsToFile(data);
    return post;
  }
}

async function updateExistingPost(id, updates) {
  if (useSupabase) {
    return await supabase.updatePost(id, updates);
  } else {
    const data = loadPostsFromFile();
    const idx = data.posts.findIndex(p => p.id === id);
    if (idx === -1) return null;
    data.posts[idx] = { ...data.posts[idx], ...updates };
    savePostsToFile(data);
    return data.posts[idx];
  }
}

async function deleteExistingPost(id) {
  if (useSupabase) {
    return await supabase.deletePost(id);
  } else {
    const data = loadPostsFromFile();
    data.posts = data.posts.filter(p => p.id !== id);
    savePostsToFile(data);
    return true;
  }
}

// ============================================
// API Routes
// ============================================

// GET all posts
app.get('/api/posts', async (req, res) => {
  try {
    const posts = await getAllPosts({ status: req.query.status });
    res.json({ posts });
  } catch (err) {
    console.error('Error loading posts:', err);
    res.status(500).json({ error: err.message });
  }
});

// GET single post
app.get('/api/posts/:id', async (req, res) => {
  try {
    const post = await getPostById(req.params.id);
    if (!post) return res.status(404).json({ error: 'Post not found' });
    res.json(post);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST create new post
app.post('/api/posts', async (req, res) => {
  try {
    console.log('POST /api/posts - body:', JSON.stringify(req.body));
    
    // Handle both JSON body and form data
    const body = req.body || {};
    
    // Convert Google Drive URL if provided
    let imageUrl = body.imageUrl || body.image || null;
    if (imageUrl && typeof imageUrl === 'string') {
      imageUrl = supabase.convertGoogleDriveUrl(imageUrl);
    }

    // Handle platforms - could be string (from form) or array (from JSON)
    let platforms = body.platforms || [];
    if (typeof platforms === 'string') {
      try {
        platforms = JSON.parse(platforms);
      } catch (e) {
        platforms = [platforms];
      }
    }
    if (!Array.isArray(platforms)) {
      platforms = [];
    }

    const post = {
      id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
      caption: body.caption || '',
      image_url: imageUrl,
      platforms: platforms,
      scheduled_for: body.scheduledFor || null,
      status: 'pending',
      created_by: body.createdBy || 'fiona',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      reviewed_by: null,
      reviewed_at: null,
      review_notes: null,
      late_id: null,
      published_at: null
    };

    console.log('Creating post:', JSON.stringify(post));
    const created = await createNewPost(post);
    res.status(201).json(created);
  } catch (err) {
    console.error('Error creating post:', err);
    res.status(500).json({ error: err.message });
  }
});

// PUT update post
app.put('/api/posts/:id', async (req, res) => {
  try {
    const post = await getPostById(req.params.id);
    if (!post) return res.status(404).json({ error: 'Post not found' });

    if (post.status !== 'pending' && post.status !== 'rejected') {
      return res.status(400).json({ error: 'Can only edit pending or rejected posts' });
    }

    // Convert Google Drive URL if provided
    let imageUrl = req.body.imageUrl || req.body.image;
    if (imageUrl) {
      imageUrl = supabase.convertGoogleDriveUrl(imageUrl);
    }

    const updates = {
      caption: req.body.caption || post.caption,
      platforms: req.body.platforms || post.platforms,
      scheduled_for: req.body.scheduledFor || post.scheduled_for,
      updated_at: new Date().toISOString()
    };

    if (imageUrl) {
      updates.image_url = imageUrl;
    }

    // Resubmit rejected post
    if (post.status === 'rejected' && req.body.resubmit) {
      updates.status = 'pending';
      updates.reviewed_by = null;
      updates.reviewed_at = null;
      updates.review_notes = null;
    }

    const updated = await updateExistingPost(req.params.id, updates);
    res.json(updated);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST approve post
app.post('/api/posts/:id/approve', async (req, res) => {
  try {
    const post = await getPostById(req.params.id);
    if (!post) return res.status(404).json({ error: 'Post not found' });

    // Prevent duplicate approvals (idempotency check)
    if (post.status === 'approved' || post.status === 'published') {
      console.log(`Post ${req.params.id} already ${post.status}, ignoring duplicate approval`);
      return res.json(post); // Return existing post without error
    }

    let updates = {
      status: 'approved',
      reviewed_by: req.body.reviewedBy || 'chris',
      reviewed_at: new Date().toISOString(),
      review_notes: req.body.notes || null,
      updated_at: new Date().toISOString()
    };

    // Push to Late if configured
    if (late.isConfigured()) {
      try {
        // Ensure caption is passed correctly
        const captionText = post.caption || '';
        console.log('Post caption from DB:', JSON.stringify(captionText));
        
        const publishData = {
          caption: captionText,
          imageUrl: post.image_url,
          platforms: post.platforms,
          scheduledFor: post.scheduled_for
        };
        console.log('Publishing to Late with data:', JSON.stringify(publishData));
        
        const result = await late.publishPost(publishData);

        updates.late_id = result.id;
        updates.status = 'published';
        updates.published_at = new Date().toISOString();
        console.log('Published to Late successfully:', result);
      } catch (err) {
        console.error('Late publish failed:', err.message);
        // Still approved, just not auto-published
      }
    }

    const updated = await updateExistingPost(req.params.id, updates);
    res.json(updated);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST reject post
app.post('/api/posts/:id/reject', async (req, res) => {
  try {
    const post = await getPostById(req.params.id);
    if (!post) return res.status(404).json({ error: 'Post not found' });

    const updates = {
      status: 'rejected',
      reviewed_by: req.body.reviewedBy || 'chris',
      reviewed_at: new Date().toISOString(),
      review_notes: req.body.notes || 'No feedback provided',
      updated_at: new Date().toISOString()
    };

    const updated = await updateExistingPost(req.params.id, updates);
    res.json(updated);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE post
app.delete('/api/posts/:id', async (req, res) => {
  try {
    const post = await getPostById(req.params.id);
    if (post && post.status === 'published') {
      return res.status(400).json({ error: 'Cannot delete published posts' });
    }

    await deleteExistingPost(req.params.id);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET dashboard stats
app.get('/api/stats', async (req, res) => {
  try {
    const posts = await getAllPosts();
    const stats = {
      total: posts.length,
      pending: posts.filter(p => p.status === 'pending').length,
      approved: posts.filter(p => p.status === 'approved').length,
      rejected: posts.filter(p => p.status === 'rejected').length,
      published: posts.filter(p => p.status === 'published').length
    };
    res.json(stats);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET storage status
app.get('/api/storage/status', (req, res) => {
  res.json({
    mode: useSupabase ? 'supabase' : 'file',
    persistent: useSupabase,
    message: useSupabase 
      ? 'Using Supabase - data persists across restarts' 
      : 'Using file storage - data will be lost on restart'
  });
});

// GET Late/Buffer status
app.get('/api/buffer/status', async (req, res) => {
  if (late.isConfigured()) {
    try {
      const accounts = await late.getAccounts();
      res.json({
        connected: true,
        service: 'late',
        profiles: accounts.accounts || accounts
      });
    } catch (err) {
      res.json({
        connected: true,
        service: 'late',
        error: err.message,
        profiles: []
      });
    }
  } else {
    res.json({
      connected: false,
      service: null,
      profiles: []
    });
  }
});

// ============================================
// Canva OAuth (unchanged)
// ============================================
const CANVA_CLIENT_ID = process.env.CANVA_CLIENT_ID || 'OC-AZxYeHya5Ie1';
const CANVA_CLIENT_SECRET = process.env.CANVA_CLIENT_SECRET || null;
const CANVA_REDIRECT_URI = 'https://thht-social.onrender.com/auth/canva/callback';
const CANVA_TOKEN_FILE = path.join(__dirname, 'data', 'canva-token.json');
const CANVA_VERIFIER_FILE = path.join(__dirname, 'data', 'canva-verifier.json');

function generateCodeVerifier() {
  return crypto.randomBytes(32).toString('base64url');
}

function generateCodeChallenge(verifier) {
  return crypto.createHash('sha256').update(verifier).digest('base64url');
}

app.get('/auth/canva', (req, res) => {
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = generateCodeChallenge(codeVerifier);
  
  fs.writeFileSync(CANVA_VERIFIER_FILE, JSON.stringify({ 
    verifier: codeVerifier,
    created: new Date().toISOString()
  }));
  
  const scopes = [
    'folder:write', 'comment:write', 'folder:permission:read',
    'brandtemplate:content:read', 'design:content:read', 'app:read',
    'brandtemplate:meta:read', 'design:content:write', 'folder:read',
    'design:permission:read', 'comment:read', 'asset:read',
    'profile:read', 'asset:write'
  ].join(' ');
  
  const authUrl = `https://www.canva.com/api/oauth/authorize?` +
    `code_challenge_method=s256&` +
    `response_type=code&` +
    `client_id=${CANVA_CLIENT_ID}&` +
    `redirect_uri=${encodeURIComponent(CANVA_REDIRECT_URI)}&` +
    `scope=${encodeURIComponent(scopes)}&` +
    `code_challenge=${codeChallenge}`;
  
  res.redirect(authUrl);
});

app.get('/auth/canva/callback', async (req, res) => {
  const { code, error } = req.query;
  
  if (error) return res.status(400).send(`Canva OAuth error: ${error}`);
  if (!code) return res.status(400).send('No authorization code received');
  
  if (!CANVA_CLIENT_SECRET) {
    return res.send(`
      <html><head><title>Canva Connected!</title></head>
      <body style="font-family: sans-serif; padding: 40px; text-align: center;">
        <h1>✅ Canva Authorization Received!</h1>
        <p>Add CANVA_CLIENT_SECRET to Render env vars to complete setup.</p>
        <p><a href="/">← Back to Dashboard</a></p>
      </body></html>
    `);
  }
  
  try {
    let codeVerifier = null;
    if (fs.existsSync(CANVA_VERIFIER_FILE)) {
      const verifierData = JSON.parse(fs.readFileSync(CANVA_VERIFIER_FILE, 'utf8'));
      codeVerifier = verifierData.verifier;
    }
    
    if (!codeVerifier) {
      return res.status(400).send('No code verifier found. Start auth from /auth/canva');
    }
    
    const tokenRes = await fetch('https://api.canva.com/rest/v1/oauth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code, client_id: CANVA_CLIENT_ID, client_secret: <REDACTED:CREDENTIAL>,
        redirect_uri: CANVA_REDIRECT_URI, code_verifier: codeVerifier
      })
    });
    
    if (!tokenRes.ok) throw new Error(`Token exchange failed: ${await tokenRes.text()}`);
    
    const tokenData = await tokenRes.json();
    fs.writeFileSync(CANVA_TOKEN_FILE, JSON.stringify({ ...tokenData, obtained_at: new Date().toISOString() }, null, 2));
    
    res.send(`
      <html><head><title>Canva Connected!</title></head>
      <body style="font-family: sans-serif; padding: 40px; text-align: center;">
        <h1>✅ Canva Connected Successfully!</h1>
        <p>Fiona can now import designs directly from Canva.</p>
        <p><a href="/">← Back to Dashboard</a></p>
      </body></html>
    `);
  } catch (err) {
    console.error('Canva OAuth error:', err);
    res.status(500).send(`OAuth error: ${err.message}`);
  }
});

app.get('/api/canva/status', (req, res) => {
  const hasToken = <REDACTED:CREDENTIAL>(CANVA_TOKEN_FILE);
  res.json({ connected: hasToken, clientId: CANVA_CLIENT_ID });
});

// ============================================
// Start Server
// ============================================
app.listen(PORT, '0.0.0.0', () => {
  console.log(`THHT Social Dashboard running on port ${PORT}`);
  console.log(`Storage: ${useSupabase ? '✅ Supabase (persistent)' : '⚠️ File (ephemeral)'}`);
});
