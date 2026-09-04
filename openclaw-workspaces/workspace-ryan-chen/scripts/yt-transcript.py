#!/usr/bin/env python3
"""
YouTube Transcript Extractor
Uses youtube_transcript_api to fetch transcripts directly (no audio download needed)
"""

import sys
import re
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_url, language='en'):
    """Fetch transcript from YouTube video"""
    video_id = extract_video_id(video_url)
    if not video_id:
        print(f"❌ Could not extract video ID from: {video_url}")
        return None
    
    print(f"📺 Video ID: {video_id}")
    
    api = YouTubeTranscriptApi()
    
    try:
        # List available transcripts
        transcripts = api.list(video_id)
        print(f"📝 Available transcripts: {transcripts}")
        
        # Fetch the transcript
        result = api.fetch(video_id, languages=[language, 'en', 'en-US'])
        
        # Extract text from snippets
        text_parts = []
        for snippet in result.snippets:
            text = snippet.text.replace('\n', ' ').strip()
            if text:
                text_parts.append(text)
        
        full_text = ' '.join(text_parts)
        
        # Clean up common artifacts
        full_text = re.sub(r'\[♪+\]', '', full_text)  # Remove music symbols
        full_text = re.sub(r'♪[^♪]*♪', '', full_text)  # Remove lyrics markers
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        
        return {
            'video_id': video_id,
            'transcript': full_text,
            'language': language
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: yt-transcript.py <youtube_url_or_id> [output_file] [language]")
        print("\nExamples:")
        print("  yt-transcript.py https://www.youtube.com/watch?v=VIDEO_ID")
        print("  yt-transcript.py VIDEO_ID output.txt")
        print("  yt-transcript.py VIDEO_ID output.txt en")
        sys.exit(1)
    
    video_url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    language = sys.argv[3] if len(sys.argv) > 3 else 'en'
    
    result = get_transcript(video_url, language)
    
    if result:
        transcript = result['transcript']
        print(f"\n{'='*60}")
        print(f"✅ Transcript ({len(transcript)} chars)")
        print(f"{'='*60}\n")
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(transcript)
            print(f"💾 Saved to: {output_file}")
        else:
            # Print preview
            preview = transcript[:1000]
            print(preview + ("..." if len(transcript) > 1000 else ""))
            
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
