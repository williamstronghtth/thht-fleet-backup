# Skill: color-grading

**When to use:** Lumetri questions, footage looks flat/washed-out/wrong, LOG or D-Log M grading, LUTs won't show up or look wrong, matching drone to camera, delivering correct color to YouTube.

## First question: is it LOG footage?
Flat, grey, low-contrast drone footage is almost always **ungraded D-Log M**, not a bug. The DJI Mini 4 Pro shoots D-Log M specifically to be graded. The fix is a color pipeline, not a "repair."

## D-Log M → Rec.709 pipeline (Chris's drone)
1. Select the drone clip → **Lumetri Color** panel.
2. **Basic Correction > Input LUT** → load DJI's **D-Log M → Rec.709** LUT (DJI provides these; install path below). This is the technical/input transform.
3. Fine-tune exposure/contrast/white balance in Basic Correction *after* the LUT.
4. Grade creatively in **Creative / Curves / Color Wheels** on top.
5. Confirm on **Lumetri Scopes** (`Window > Lumetri Scopes`): keep luma roughly 0–100 IRE, watch the Waveform/RGB Parade so nothing clips illegally for Rec.709.

## LUT install paths (so they appear in Lumetri dropdowns)
- **Input/Technical dropdown:** `...\Adobe Premiere Pro <ver>\Lumetri\LUTs\Technical`
- **Creative dropdown:** `...\Adobe Premiere Pro <ver>\Lumetri\LUTs\Creative`
- **Per-user:** `%AppData%\Adobe\Common\LUTs\Technical` (or `\Creative`)
- Restart Premiere after adding a LUT. If it's not in the dropdown, use **Browse…** to load it directly.

## Matching 70D to drone
The 70D shoots a fairly baked Rec.709-ish image; the drone is LOG. Grade the **drone up to match the 70D**, not the other way around: neutralize D-Log M first, then match white balance, contrast, and saturation using the scopes (compare Waveform + Vectorscope between clips). **Color Match** (`Lumetri > Color Wheels & Match > Comparison View`) can auto-align a shot to a reference frame.

## Delivery / color management
- Deliver **Rec.709 (SDR)** for YouTube. Don't accidentally ship an HDR/Rec.2020 tag from HLG/HDR sources — check `File > Project Settings > Color Management` and the sequence's working color space.
- If the whole timeline looks off only after a Premiere update, suspect a **color-management/working-space** change, not the grade.

## Brand color reference (for graphics, not grading)
Cobalt `#2563A9`, Sunflower `#F7C948`. These are for titles/lower-thirds (Essential Graphics), applied in sRGB — don't confuse graphics color with footage grading.

## Common gotchas
- **LUT applied twice** (Input LUT *and* Creative LUT both D-Log M) → oversaturated/crushed. Use the transform once.
- **Washed out after export but fine in Premiere** → gamma/color-space mismatch; check export color settings target Rec.709.
