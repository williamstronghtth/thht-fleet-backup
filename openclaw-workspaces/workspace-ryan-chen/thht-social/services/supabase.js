/**
 * Supabase Client for thht-social
 * Handles persistent storage for posts
 */

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_ANON_KEY;

/**
 * Check if Supabase is configured
 */
function isConfigured() {
  return !!(SUPABASE_URL && SUPABASE_KEY);
}

/**
 * Make authenticated request to Supabase
 */
async function supabaseRequest(endpoint, options = {}) {
  if (!isConfigured()) {
    throw new Error('Supabase not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.');
  }

  const url = `${SUPABASE_URL}/rest/v1${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'apikey': <REDACTED:CREDENTIAL>,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': options.prefer || 'return=representation',
      ...options.headers
    }
  });

  if (!res.ok) {
    const error = await res.text();
    throw new Error(`Supabase error: ${res.status} - ${error}`);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

/**
 * Get all posts
 */
async function getPosts(filters = {}) {
  let endpoint = '/posts?order=created_at.desc';
  
  if (filters.status) {
    endpoint += `&status=eq.${filters.status}`;
  }
  
  return supabaseRequest(endpoint);
}

/**
 * Get single post by ID
 */
async function getPost(id) {
  const result = await supabaseRequest(`/posts?id=eq.${id}`);
  return result && result.length > 0 ? result[0] : null;
}

/**
 * Create a new post
 */
async function createPost(post) {
  const result = await supabaseRequest('/posts', {
    method: 'POST',
    body: JSON.stringify(post)
  });
  return result && result.length > 0 ? result[0] : result;
}

/**
 * Update a post
 */
async function updatePost(id, updates) {
  const result = await supabaseRequest(`/posts?id=eq.${id}`, {
    method: 'PATCH',
    body: JSON.stringify(updates)
  });
  return result && result.length > 0 ? result[0] : result;
}

/**
 * Delete a post
 */
async function deletePost(id) {
  return supabaseRequest(`/posts?id=eq.${id}`, {
    method: 'DELETE'
  });
}

/**
 * Convert Google Drive sharing URL to direct URL
 * Input:  https://drive.google.com/file/d/FILE_ID/view?usp=sharing
 * Output: https://drive.google.com/uc?export=view&id=FILE_ID
 */
function convertGoogleDriveUrl(url) {
  if (!url || typeof url !== 'string') return url || null;
  
  // Already a direct link
  if (url.includes('drive.google.com/uc?')) {
    return url;
  }
  
  // Extract file ID from various Google Drive URL formats
  const patterns = [
    /drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)/,
    /drive\.google\.com\/open\?id=([a-zA-Z0-9_-]+)/,
    /docs\.google\.com\/.*\/d\/([a-zA-Z0-9_-]+)/
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match && match[1]) {
      return `https://drive.google.com/uc?export=view&id=${match[1]}`;
    }
  }
  
  // Not a Google Drive URL, return as-is
  return url;
}

module.exports = {
  isConfigured,
  getPosts,
  getPost,
  createPost,
  updatePost,
  deletePost,
  convertGoogleDriveUrl
};
