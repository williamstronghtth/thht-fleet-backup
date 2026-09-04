# Skill: export-delivery

**When to use:** Anything about exporting/rendering — export hangs or fails, wrong file size/quality, "what settings for YouTube," Media Encoder vs direct export, NVENC/hardware-encode problems.

## THHT delivery defaults (memorize these)
- **Codec:** H.264 (H.265/HEVC only if 4K file size matters and the destination supports it)
- **Format:** YouTube, **Rec.709 (SDR)**
- **1080p:** VBR **2-pass**, Target ~**16 Mbps**, Max ~**24 Mbps**
- **4K:** VBR **2-pass**, Target ~**45 Mbps**, Max ~**68 Mbps**
- **Audio:** AAC, 320 kbps, 48 kHz; loudness ~ **-14 LUFS** (YouTube normalizes to this — matching it avoids surprise volume changes)
- **Match Source** for frame rate/resolution unless intentionally changing it.

## Export failing or hanging (e.g., stuck at 92%)
Diagnose in this order:
1. **Where does it stall?** A consistent frozen % almost always = **one bad frame/clip/effect at that timecode**. Move the playhead there — look for a corrupt clip, a heavy plugin, or a Dynamic Link (After Effects) comp.
2. **Hardware vs software encoding:** `Export settings > Encoding Settings > Performance` → switch **Hardware Encoding (NVENC)** ↔ **Software Encoding**. NVENC has driver-specific bugs; software encoding is slower but rules it out.
3. **Queue to Media Encoder instead of direct export** (or vice-versa). Media Encoder is often more robust for long/heavy exports and keeps Premiere free. Use the **Queue** button, not **Export**.
4. **Render in/out first** (`Sequence > Render In to Out`) so playback previews exist — turns a fragile export into a copy operation and surfaces the bad frame early.
5. **Smart rendering / mismatch:** if source and export codecs match, smart rendering can pass through — but a codec mismatch mid-timeline can choke. Consider transcoding the offending source.
6. **GPU/driver:** export crashes tie back to the GPU driver more than anything — Studio driver, or toggle renderer to Software Only as a test (see premiere-diagnostics).

## Common error patterns
- **"Error compiling movie" / "Unknown error"** → almost always a specific spot on the timeline. Binary-search: export the first half, then second half, to find the clip; then transcode or replace it.
- **Export succeeds but audio/video drift** → source is likely VFR or a sample-rate mismatch (see audio-troubleshooting / proxy-and-media).
- **Huge file / poor quality** → wrong bitrate mode; use VBR 2-pass with the targets above, not CBR or a single low pass.

## Chris-specific
Mixed 70D + drone timelines: confirm the **sequence** frame rate is what he wants delivered, and that H.265 drone clips aren't forcing a slow software decode during export (a transcode/proxy pass can make a hanging export finish cleanly).
