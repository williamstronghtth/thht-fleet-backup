/**
 * Ayrshare API Integration
 * https://www.ayrshare.com/docs
 * 
 * Handles posting to Instagram, Facebook, Twitter, LinkedIn
 */

const AYRSHARE_API_URL = 'https://api.ayrshare.com/api';
const AYRSHARE_API_KEY = process.env.AYRSHARE_API_KEY || null;

/**
 * Check if Ayrshare is configured
 */
function isConfigured() {
  return !!AYRSHARE_API_KEY;
}

/**
 * Get connected social profiles
 */
async function getProfiles() {
  if (!isConfigured()) {
    throw new Error('Ayrshare API key not configured');
  }

  const res = await fetch(`${AYRSHARE_API_URL}/user`, {
    headers: {
      'Authorization': `Bearer ${AYRSHARE_API_KEY}`
    }
  });

  if (!res.ok) {
    throw new Error(`Ayrshare API error: ${res.status}`);
  }

  const data = await res.json();
  return data.activeSocialAccounts || [];
}

/**
 * Post to social media platforms
 * @param {Object} post - Post data
 * @param {string} post.caption - Post text/caption
 * @param {string} post.imageUrl - Public URL to image (Ayrshare needs accessible URL)
 * @param {string[]} post.platforms - Array of platforms: 'instagram', 'facebook', 'twitter', 'linkedin'
 * @param {Date} post.scheduledFor - Optional scheduled time
 */
async function publishPost(post) {
  if (!isConfigured()) {
    throw new Error('Ayrshare API key not configured');
  }

  // Map our platform names to Ayrshare's
  const platformMap = {
    'instagram': 'instagram',
    'facebook': 'facebook',
    'twitter': 'twitter',
    'linkedin': 'linkedin'
  };

  const platforms = post.platforms.map(p => platformMap[p]).filter(Boolean);

  if (platforms.length === 0) {
    throw new Error('No valid platforms specified');
  }

  const body = {
    post: post.caption,
    platforms: platforms
  };

  // Add image if provided
  if (post.imageUrl) {
    body.mediaUrls = [post.imageUrl];
  }

  // Add scheduling if provided
  if (post.scheduledFor) {
    body.scheduleDate = new Date(post.scheduledFor).toISOString();
  }

  const res = await fetch(`${AYRSHARE_API_URL}/post`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${AYRSHARE_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(`Ayrshare post failed: ${error.message || res.status}`);
  }

  const result = await res.json();
  
  return {
    success: true,
    id: result.id,
    postIds: result.postIds || {},
    status: result.status
  };
}

/**
 * Delete a scheduled post
 * @param {string} postId - Ayrshare post ID
 */
async function deletePost(postId) {
  if (!isConfigured()) {
    throw new Error('Ayrshare API key not configured');
  }

  const res = await fetch(`${AYRSHARE_API_URL}/post/${postId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${AYRSHARE_API_KEY}`
    }
  });

  return res.ok;
}

/**
 * Get post history
 */
async function getHistory(limit = 20) {
  if (!isConfigured()) {
    throw new Error('Ayrshare API key not configured');
  }

  const res = await fetch(`${AYRSHARE_API_URL}/history?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${AYRSHARE_API_KEY}`
    }
  });

  if (!res.ok) {
    throw new Error(`Ayrshare API error: ${res.status}`);
  }

  return res.json();
}

/**
 * Upload media to Ayrshare (returns URL)
 * Used when we need to host images for posting
 */
async function uploadMedia(buffer, filename, contentType) {
  if (!isConfigured()) {
    throw new Error('Ayrshare API key not configured');
  }

  const formData = new FormData();
  formData.append('file', new Blob([buffer], { type: contentType }), filename);

  const res = await fetch(`${AYRSHARE_API_URL}/media/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${AYRSHARE_API_KEY}`
    },
    body: formData
  });

  if (!res.ok) {
    throw new Error(`Media upload failed: ${res.status}`);
  }

  const data = await res.json();
  return data.url;
}

module.exports = {
  isConfigured,
  getProfiles,
  publishPost,
  deletePost,
  getHistory,
  uploadMedia
};
