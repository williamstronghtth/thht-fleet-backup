# Skill: audio-troubleshooting

**When to use:** Audio out of sync, drift, no audio, crackle/dropouts, levels too quiet/loud, voiceover cleanup, loudness for YouTube, ASIO/hardware issues on Windows.

## Sync & drift (the classic)
Distinguish two failure modes — they have different causes:
- **Constant offset** (audio a fixed amount ahead/behind the whole time) → usually a simple slip; select audio, nudge, or re-sync. Often from a hardware capture delay.
- **Progressive drift** (starts in sync, slowly separates — worst by the end, or "only after Dynamic Link / long export") → almost always **variable frame rate (VFR)** source or a **sample-rate mismatch**. This is the one people blame Premiere for.

Diagnose drift:
1. **Check the source frame rate** — phone/screen recordings are often VFR. Premiere assumes CFR, so audio slowly desyncs. **Fix: transcode to constant frame rate** (HandBrake or Media Encoder to an intermediate) before editing. See proxy-and-media.
2. **Check sample rate** — mismatched 44.1 kHz vs 48 kHz between clips/sequence causes drift and pitch issues. Standardize on **48 kHz** (video standard). Set sequence audio to 48k; conform stray 44.1k clips.
3. **Dynamic Link (Audition/AE)** round-trips can introduce offset — if drift appears only after DL, **render-and-replace** instead of keeping the live link.

## Levels & loudness (YouTube)
- Target ~ **-14 LUFS** integrated (YouTube's normalization point). Under-shooting means YouTube leaves it quiet; matching it keeps your mix intact.
- Use **Essential Sound** panel: tag clips as Dialogue / Music / SFX / Ambience, then use **Loudness > Auto-Match**, and **Ducking** to duck music under voiceover automatically.
- Watch the **Loudness Radar** / audio meters; keep peaks below 0 dBFS (aim ~ -1 dBTP true peak).

## No audio / dropouts / crackle (Windows)
1. **Audio hardware:** `Edit > Preferences > Audio Hardware` → confirm the right **Default Output** device and, if using an interface, the correct **ASIO** driver. Wrong device = "no sound."
2. **Crackle/dropouts on playback:** raise the **I/O Buffer Size** in Audio Hardware; clear media cache; render audio previews.
3. **Muted/soloed track or track targeting** — check the timeline's M/S buttons and that the audio track is enabled.
4. **Sample-rate mismatch between the interface and the project** also causes crackle — match them.

## Chris-specific
Voiceover + licensed music beds + camera audio: use Essential Sound ducking so the music dips under Chris's narration, normalize the whole thing to -14 LUFS for YouTube, and keep everything at 48 kHz to avoid drift across the mixed 70D/drone sources.
