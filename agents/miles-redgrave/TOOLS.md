# TOOLS.md — Miles's Local Notes

## My channel
- **Telegram → Chris:** chat id `8560812913`. My bot token is looked up from `/root/agents/telegram-bots.json` by `run-agent.sh` (agent_id `miles-redgrave`).

## Key file locations I reference constantly (on Chris's Windows machine)
- **Preferences / crash logs:** `%AppData%\Adobe\Premiere Pro\<version>\`
- **Media cache:** set in `Edit > Preferences > Media Cache` (default under `%AppData%\...\Common\`)
- **LUTs (so they show in Lumetri's dropdown):**
  - `C:\Program Files\Adobe\Adobe Premiere Pro <ver>\Lumetri\LUTs\Creative` (Creative dropdown)
  - or `...\Lumetri\LUTs\Technical` (Input/Technical dropdown)
  - per-user: `%AppData%\...\Common\LUTs`
- **Auto-Save:** location set in `Edit > Preferences > Auto Save`; recovers `.prproj` snapshots

## Handy launch tricks
- **Reset preferences:** hold **Alt** during launch (release after splash)
- **Reset prefs + plugin cache:** hold **Alt + Shift** during launch
- **Open a specific project bypassing the Home screen:** double-click the `.prproj` directly

## Delivery defaults for THHT (memorize)
- **YouTube 1080p:** H.264, VBR 2-pass, target ~16 Mbps / max ~24 Mbps, Rec.709
- **YouTube 4K:** H.264 (or HEVC), VBR 2-pass, target ~45 Mbps / max ~68 Mbps
- **Loudness:** normalize to ~ **-14 LUFS** (YouTube target)
- **Color:** deliver **Rec.709** (SDR)

## Team contacts (inbox paths)
- William (management hub): `/root/agents/william-strong/workspace/inbox/` (agent id `main`)
- Fiona (social): `/root/agents/fiona-murphy/workspace/inbox/`
- Iris (creative): `/root/agents/iris-vale/workspace/inbox/`

_Add environment-specific notes here as I learn Chris's exact setup (Premiere version, GPU model + driver, drive layout)._
