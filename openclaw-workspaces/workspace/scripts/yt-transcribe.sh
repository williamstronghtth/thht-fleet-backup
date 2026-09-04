#!/bin/bash
# YouTube Audio Transcriber
# Downloads audio, transcribes, deletes audio, keeps transcript
# Usage: ./yt-transcribe.sh <youtube_url> [output_name]

set -e

URL="$1"
NAME="${2:-transcript}"
WORK_DIR="/tmp/yt-transcribe"
OUTPUT_DIR="/root/.openclaw/workspace/transcripts"

mkdir -p "$WORK_DIR" "$OUTPUT_DIR"

echo "📥 Downloading audio from: $URL"
yt-dlp -x --audio-format mp3 --audio-quality 0 \
    -o "$WORK_DIR/audio.%(ext)s" \
    --no-playlist \
    "$URL"

AUDIO_FILE="$WORK_DIR/audio.mp3"

if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ Audio download failed"
    exit 1
fi

echo "🎙️ Transcribing..."
python3 << EOF
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("$AUDIO_FILE", beam_size=5)

print(f"Detected language: {info.language} (probability {info.language_probability:.2f})")

with open("$OUTPUT_DIR/${NAME}.md", "w") as f:
    f.write(f"# Transcript: ${NAME}\n")
    f.write(f"Source: $URL\n")
    f.write(f"Language: {info.language}\n\n")
    f.write("---\n\n")
    
    for segment in segments:
        timestamp = f"[{int(segment.start//60):02d}:{int(segment.start%60):02d}]"
        f.write(f"{timestamp} {segment.text.strip()}\n")
        print(f"{timestamp} {segment.text.strip()[:80]}...")

print(f"\n✅ Saved to: $OUTPUT_DIR/${NAME}.md")
EOF

echo "🗑️ Cleaning up audio file..."
rm -f "$AUDIO_FILE"
rm -rf "$WORK_DIR"

echo "✅ Done! Transcript saved, audio deleted."
