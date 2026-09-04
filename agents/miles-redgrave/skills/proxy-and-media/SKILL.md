# Skill: proxy-and-media

**When to use:** Laggy/choppy playback, heavy 4K/H.265 footage, VFR footage, proxy setup or proxy/full-res toggle problems, media cache issues, offline/missing media, relinking.

## Proxies (the fix for sluggish 4K/H.265 playback)
The Mini 4 Pro's 4K H.265 is expensive to decode on Windows — proxies are usually the real answer to stutter, not new hardware.
1. **Create proxies:** in the Project panel, select clips → right-click → **Proxy > Create Proxies**. Pick a light preset (e.g. **H.264 low / 1024x540** or **ProRes Proxy**). Media Encoder generates them.
2. **Attach existing proxies:** right-click → **Proxy > Attach Proxies** if they already exist.
3. **Toggle proxy/full-res playback:** add the **Toggle Proxies** button to the Program monitor (the **+** button editor). Editing uses proxies; **export always uses full-res automatically** — a common worry, but you don't lose quality.
4. **Ingest on import:** `File > Project Settings > Ingest` → auto-create proxies as footage is imported.

### Proxy gotchas
- **Resolution/aspect mismatch** between proxy and source → shifted/zoomed image. Regenerate proxies with a matching aspect ratio.
- Proxy toggle greyed out → the proxy media went offline; relink or recreate.

## Transcoding vs proxies
- **Proxies:** keep originals, edit light, auto-swap to full-res on export. Best default for Chris.
- **Transcode to intermediate (DNxHR / ProRes):** replaces the working media entirely. Use when the source is problematic (VFR, weird codec) or for maximum timeline stability. `Media Encoder` or `Ingest > Transcode`.

## Variable frame rate (VFR) — the hidden villain
Phone clips and screen recordings are often VFR. Premiere treats them as CFR → **audio slowly drifts out of sync**. Fix: **transcode VFR → CFR** (HandBrake, or Media Encoder to ProRes/DNxHR) *before* editing. Suspect this any time "audio desync gets worse toward the end."

## Media cache
- Corrupt cache → phantom glitches, wrong thumbnails, import failures, playback artifacts.
- `Edit > Preferences > Media Cache` → **Delete unused / Clean**. Set the cache to a fast local drive, not a network/slow drive.
- Periodically clear it; it grows unbounded.

## Offline / missing media & relinking
- Red "Media Offline" → `File > Link Media` (or right-click the offline clip → **Link Media**). Point it at the moved file; Premiere relinks the rest in that folder automatically if names match.
- **Prevent it:** keep a sane drive structure and use **Consolidate & Transcode** / **Project Manager** to collect all media into one folder for archiving (see project-recovery).

## Frame-rate mismatch (Chris's mixed rig)
70D and Mini 4 Pro can be different fps. Choppy motion = clip fps ≠ sequence fps. Set the sequence to the intended delivery fps; if a clip's fps is misread, right-click → **Modify > Interpret Footage > Assume this frame rate**.
