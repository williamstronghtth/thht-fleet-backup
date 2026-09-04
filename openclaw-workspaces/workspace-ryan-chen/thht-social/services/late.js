/**
 * Late API Integration
 * https://docs.getlate.dev
 * 
 * Handles posting to Instagram, Facebook, Twitter, LinkedIn
 */

const LATE_API_URL = 'https://getlate.dev/api/v1';
const LATE_API_KEY = process.env.LATE_API_KEY || null;

/**
 * Check if Late is configured
 */
function isConfigured() {
  return !!LATE_API_KEY;
}

/**
 * Make authenticated request to Late API
 */
async function lateRequest(endpoint, options = {}) {
  if (!isConfigured()) {
    throw new Error('Late API key not configured');
  }

  const url = `${LATE_API_URL}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${LATE_API_KEY}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: `HTTP ${res.status}` }));
    throw new Error(`Late API error: ${error.message || error.error || res.status}`);
  }

  return res.json();
}

/**
 * Get connected profiles and accounts
 */
async function getProfiles() {
  return lateRequest('/profiles');
}

/**
 * Get connected social accounts
 */
async function getAccounts() {
  return lateRequest('/accounts');
}

/**
 * Upload media to Late (returns media URL/ID for posting)
 * @param {Buffer} buffer - File buffer
 * @param {string} filename - Original filename
 * @param {string} contentType - MIME type
 */
async function uploadMedia(buffer, filename, contentType) {
  if (!isConfigured()) {
    throw new Error('Late API key not configured');
  }

  const formData = new FormData();
  formData.append('file', new Blob([buffer], { type: contentType }), filename);

  const res = await fetch(`${LATE_API_URL}/media`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${LATE_API_KEY}`
    },
    body: formData
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: `HTTP ${res.status}` }));
    throw new Error(`Media upload failed: ${error.message || res.status}`);
  }

  return res.json();
}

/**
 * Create a post on Late
 * @param {Object} post - Post data
 * @param {string} post.text - Post caption/text
 * @param {string[]} post.platforms - Array: 'instagram', 'facebook', 'twitter', 'linkedin'
 * @param {string} post.mediaUrl - URL to media (optional)
 * @param {string} post.scheduledFor - ISO date string for scheduling (optional)
 */
async function createPost(post) {
  // Map our platform names to Late's
  const platformMap = {
    'instagram': 'instagram',
    'facebook': 'facebook',
    'twitter': 'twitter',
    'x': 'twitter',  // Support both 'x' and 'twitter'
    'linkedin': 'linkedin'
  };

  const inputPlatforms = Array.isArray(post.platforms) ? post.platforms : [];
  const platforms = inputPlatforms
    .map(p => platformMap[p.toLowerCase()])
    .filter(Boolean);

  if (platforms.length === 0) {
    throw new Error('No valid platforms specified');
  }

  // Ensure text is always a string
  const postText = String(post.text || '').trim();
  
  const body = {
    text: postText,
    platforms: platforms
  };

  console.log('Late createPost - text:', postText);
  console.log('Late createPost - platforms:', platforms);

  // Add media if provided
  if (post.mediaUrl) {
    body.media = [{ url: post.mediaUrl }];
    console.log('Late createPost - media URL:', post.mediaUrl);
  }

  // Add scheduling if provided
  if (post.scheduledFor) {
    body.scheduledFor = new Date(post.scheduledFor).toISOString();
  }

  console.log('Late createPost - full body:', JSON.stringify(body));

  return lateRequest('/posts', {
    method: 'POST',
    body: JSON.stringify(body)
  });
}

/**
 * Get post by ID
 */
async function getPost(postId) {
  return lateRequest(`/posts/${postId}`);
}

/**
 * Delete a post
 */
async function deletePost(postId) {
  return lateRequest(`/posts/${postId}`, { method: 'DELETE' });
}

/**
 * Get posting history
 */
async function getHistory(limit = 20) {
  return lateRequest(`/posts?limit=${limit}`);
}

/**
 * Publish post immediately or schedule it
 * Main function used by the approval flow
 */
async function publishPost(post) {
  if (!post) {
    throw new Error('No post data provided to publishPost');
  }
  
  const result = await createPost({
    text: post.caption || '',
    platforms: post.platforms || [],
    mediaUrl: post.imageUrl || null,
    scheduledFor: post.scheduledFor || null
  });

  return {
    success: true,
    id: result.id,
    status: result.status,
    platforms: result.platforms
  };
}

module.exports = {
  isConfigured,
  getProfiles,
  getAccounts,
  uploadMedia,
  createPost,
  getPost,
  deletePost,
  getHistory,
  publishPost
};
