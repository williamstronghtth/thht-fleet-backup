#!/bin/bash
# Social Media Posting Script - Platform Isolation + Hash Check
# Usage: ./post-social.sh <image_path> <long_text_file> <short_text_file>
#
# FIX 2026-02-22: Changed "text" to "content" — Late API requires "content" field

set -e

LATE_API_KEY="${LATE_API_KEY}"
LATE_BASE="https://getlate.dev/api/v1"

# Account IDs
INSTAGRAM="698f6a5ffd3d49fbfa3e29f7"
FACEBOOK="698f6ab9fd3d49fbfa3e2a9f"
LINKEDIN="698f6b23fd3d49fbfa3e2baf"
TWITTER="698f6ad0fd3d49fbfa3e2afd"

IMAGE_PATH="$1"
LONG_TEXT_FILE="$2"
SHORT_TEXT_FILE="$3"

if [ -z "$IMAGE_PATH" ] || [ -z "$LONG_TEXT_FILE" ]; then
    echo "Usage: $0 <image_path> <long_text_file> [short_text_file]"
    exit 1
fi

LONG_TEXT=$(cat "$LONG_TEXT_FILE")
SHORT_TEXT="${SHORT_TEXT_FILE:+$(cat "$SHORT_TEXT_FILE")}"
[ -z "$SHORT_TEXT" ] && SHORT_TEXT="${LONG_TEXT:0:277}..."

# Generate content hash (first 60 chars of text)
CONTENT_HASH=$(echo -n "${LONG_TEXT:0:60}" | md5sum | cut -d' ' -f1)
echo "Content hash: $CONTENT_HASH"

# Check for existing posts with this hash
echo "Checking for existing posts..."
EXISTING=$(curl -s -X GET "$LATE_BASE/posts?limit=20" \
    -H "Authorization: Bearer $LATE_API_KEY" | \
    python3 -c "
import json, sys
data = json.load(sys.stdin)
for p in data.get('posts', []):
    if p.get('contentHash') == '$CONTENT_HASH':
        print(f\"FOUND: {p.get('_id')} - {p.get('status')}\")
        sys.exit(1)
print('No duplicates found')
" 2>/dev/null) || {
    echo "⚠️  Duplicate content detected! Skipping post creation."
    echo "$EXISTING"
    exit 0
}

echo "$EXISTING"

# Upload image
echo ""
echo "📤 Uploading image..."
FILENAME=$(basename "$IMAGE_PATH")
PRESIGN=$(curl -s -X POST "$LATE_BASE/media/presign" \
    -H "Authorization: Bearer $LATE_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"filename\": \"$FILENAME\", \"contentType\": \"image/png\"}")

UPLOAD_URL=$(echo "$PRESIGN" | jq -r '.uploadUrl')
PUBLIC_URL=$(echo "$PRESIGN" | jq -r '.publicUrl')

curl -s -X PUT "$UPLOAD_URL" \
    -H "Content-Type: image/png" \
    --data-binary "@$IMAGE_PATH" > /dev/null

echo "✅ Image uploaded: $PUBLIC_URL"

# Batch 1: Facebook + LinkedIn
echo ""
echo "📘📊 Posting to Facebook + LinkedIn..."
RESULT1=$(curl -s -X POST "$LATE_BASE/posts" \
    -H "Authorization: Bearer $LATE_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(jq -n \
        --arg content "$LONG_TEXT" \
        --arg url "$PUBLIC_URL" \
        --arg fb "$FACEBOOK" \
        --arg li "$LINKEDIN" \
        '{
            accountIds: [$fb, $li],
            content: $content,
            mediaItems: [{type: "image", url: $url}],
            crosspostingEnabled: false
        }')")

echo "$RESULT1" | jq -r '.message // .error // "Posted"'

# Batch 2: Twitter (short version)
echo ""
echo "🐦 Posting to Twitter..."
RESULT2=$(curl -s -X POST "$LATE_BASE/posts" \
    -H "Authorization: Bearer $LATE_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(jq -n \
        --arg content "$SHORT_TEXT" \
        --arg url "$PUBLIC_URL" \
        --arg tw "$TWITTER" \
        '{
            accountIds: [$tw],
            content: $content,
            mediaItems: [{type: "image", url: $url}],
            crosspostingEnabled: false
        }')")

echo "$RESULT2" | jq -r '.message // .error // "Posted"'

# Batch 3: Instagram (isolated)
echo ""
echo "📸 Posting to Instagram..."
RESULT3=$(curl -s -X POST "$LATE_BASE/posts" \
    -H "Authorization: Bearer $LATE_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(jq -n \
        --arg content "$LONG_TEXT" \
        --arg url "$PUBLIC_URL" \
        --arg ig "$INSTAGRAM" \
        '{
            accountIds: [$ig],
            content: $content,
            mediaItems: [{type: "image", url: $url}],
            crosspostingEnabled: false
        }')")

IG_STATUS=$(echo "$RESULT3" | jq -r '.post.status // .error // "unknown"')
echo "Instagram status: $IG_STATUS"

if [ "$IG_STATUS" = "failed" ] || echo "$RESULT3" | grep -q "Duplicate content"; then
    echo "⚠️  Instagram failed (likely duplicate detection). FB/LI/TW unaffected."
fi

echo ""
echo "✅ Done! Platform-isolated posting complete."
