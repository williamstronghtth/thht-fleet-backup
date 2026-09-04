# Skill: premiere-diagnostics

**When to use:** Premiere crashes, hangs, freezes, launches to a black/blank UI, plays back choppy, or "just started acting weird." This is my master diagnostic method plus the stability/performance playbook.

## The method (never skip this)
1. **Get the facts before touching anything.** Ask for whichever of these I don't already know:
   - Exact error text / code (word-for-word or a photo)
   - Premiere version (`Help > About Premiere Pro`)
   - GPU model + driver version; NVIDIA **Studio** vs **Game Ready** driver
   - Footage: camera, codec, frame rate (70D 1080p H.264? Mini 4 Pro 4K H.265? D-Log M?)
   - **What changed recently** (update, driver, plugin, new footage, moved drive)
   - **When** it happens: on launch / playback / scrub / export / only after Dynamic Link / at a specific %
2. **Rank suspects by likelihood, test the fastest first.** State them out loud, ordered, and say what each test rules out.
3. **Fix in ordered steps** with exact paths and one-line "why" each.
4. **Confirm + record** the symptom→cause→fix in `memory/`.

## Fast, low-risk tests (in the order I usually try them)
1. **Reset preferences:** hold **Alt** while launching until the splash screen. Rebuilds prefs, does NOT touch the project. Fixes a huge share of "weird UI / won't launch / tools broken" issues.
   - Heavier: **Alt + Shift** on launch resets prefs **and** plugin cache.
2. **Clean media cache:** `Edit > Preferences > Media Cache > Remove/Delete unused`. Corrupt cache = phantom playback glitches, bad thumbnails, import weirdness.
3. **Toggle GPU renderer:** `File > Project Settings > General > Renderer` → switch between **Mercury GPU Acceleration (CUDA/OpenCL)** and **Software Only**. If Software Only is stable, it's a GPU/driver problem, not the project.
4. **Update/rollback GPU driver:** on NVIDIA, install the **Studio** driver (more stable for creative apps than Game Ready). Many "Lumetri silently broken" / export-crash bugs are a bad driver.
5. **Isolate plugins:** move third-party plugins out of the plugin folder and relaunch. If the crash stops, reintroduce one at a time.
6. **New sequence / import test:** does it crash in a *new* empty project too? Separates a corrupt project (→ project-recovery skill) from an install/driver problem.

## Where the evidence lives
- **Crash logs & prefs:** `%AppData%\Adobe\Premiere Pro\<version>\`
- Driver info: NVIDIA Control Panel / GeForce Experience → note the exact version and date.

## Chris-specific likely causes (bias toward these)
- Choppy playback with drone clips → **H.265 decode load** → proxies/transcode (see proxy-and-media), not a hardware failure.
- Stutter with mixed clips → **frame-rate mismatch** (70D vs Mini 4 Pro) → check sequence vs clip fps.
- "Reinstall" is a **last resort**, and I say *why* when I finally recommend it — never a first move.
