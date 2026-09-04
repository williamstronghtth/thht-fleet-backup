# Skill: project-recovery

**When to use:** Project won't open, "project appears to be damaged," Premiere crashes on opening a specific `.prproj`, lost work after a crash, or preparing a project for archive/handoff.

## When a project won't open / is corrupt
Work through these in order (cheapest first):
1. **Open an Auto-Save copy.** Premiere writes timestamped backups. Location: `Edit > Preferences > Auto Save` shows the folder (default: an `Adobe Premiere Pro Auto-Save` folder next to the project or in Documents). Open the **most recent** auto-save that predates the corruption — losing 15 minutes beats losing everything.
2. **Try the `.prproj` backup / previous version.** Premiere keeps the prior save; also check any versioned copies.
3. **Import the broken project into a NEW empty project:** `File > Import` → select the damaged `.prproj`. Sometimes a fresh project can pull sequences out of a file that won't open directly.
4. **A `.prproj` is gzipped XML.** As a last resort it can be un-gzipped and inspected/repaired, but attempt auto-save recovery first — it's almost always faster and safer.
5. **Corruption tied to one sequence/clip:** if it opens but crashes on a sequence, duplicate the project, delete the suspect sequence, and rebuild that part.

## Auto-Save archaeology
- Increase safety going forward: `Edit > Preferences > Auto Save` → **save every 5–10 min**, keep **20+ versions**. Cheap insurance.
- Auto-saves are full project snapshots — sort by date, open the newest good one, then **Save As** a clean new file immediately.

## Productions vs. single projects
- For big/multi-part work, **Productions** (`File > New > Production`) splits work into linked projects with shared media and locking — more resilient than one giant `.prproj`, and corruption is contained to one sub-project.
- For Chris's listing videos a single project is usually fine; suggest Productions only if projects get large or he collaborates.

## Consolidate / transcode / archive
- `File > Project Manager` → **Consolidate & Transcode** (or Collect Files) to gather all media + project into one folder. Use this to:
  - Archive a finished listing cleanly
  - Fix chronic offline-media problems (everything lives in one place)
  - Hand a project to someone else
- **Relinking** offline media: `File > Link Media` — see proxy-and-media.

## Prevention (what I tell Chris after every recovery)
1. Auto-save every 5–10 min, 20+ versions.
2. Keep media on a fast local drive with a consistent folder structure.
3. `Save As` a new version at major milestones (v01, v02…) so there's always a known-good file.
4. Clear the media cache periodically.
