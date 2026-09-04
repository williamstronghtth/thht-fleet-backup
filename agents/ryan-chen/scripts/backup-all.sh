#!/usr/bin/env bash
# backup-all.sh — Produce a sanitized, relaunch-ready archive of the whole agent fleet.
#
# WHY this exists: ~4.6GB lives on this box, but only a small slice is irreplaceable.
# Code is already on GitHub; scraped data is re-fetchable; node_modules is noise.
# What CANNOT be regenerated is agent personas, memory files, and system config.
# This script captures exactly that slice, with secrets stripped.
#
# Usage:  bash backup-all.sh [OUT_DIR]
# Output: OUT_DIR/thht-backup-YYYY-MM-DD.tar.gz + a MANIFEST.txt
#
# TODO(ryan-chen): re-run after any new agent is onboarded — 2026-09-04

set -euo pipefail

OUT_DIR="${1:-/root/agents/ryan-chen/workspace/backups}"
STAMP="$(date +%Y-%m-%d)"
STAGE="$(mktemp -d)"
BUNDLE="${STAGE}/thht-backup-${STAMP}"
ARCHIVE="${OUT_DIR}/thht-backup-${STAMP}.tar.gz"

trap 'rm -rf "${STAGE}"' EXIT

mkdir -p "${OUT_DIR}" "${BUNDLE}"

# --- Exclusions -------------------------------------------------------------
# Secrets never enter the bundle. Bulk/regenerable data never enters either.
readonly EXCLUDES=(
  --exclude=.git
  --exclude=node_modules
  --exclude=__pycache__
  --exclude=.cache
  --exclude=.venv
  --exclude=venv
  --exclude=browser_profiles
  --exclude='*.pyc'
  --exclude='*.log'
  --exclude='*.sqlite'
  --exclude='*.parquet'
  --exclude='*.zip'
  --exclude='*.tar.gz'
  # Python virtualenvs: named inconsistently across workspaces (scrapling_env,
  # kalshi_env, ...), so match the suffix rather than a fixed list. All are
  # rebuildable from requirements.txt and one of them holds a 117MB Playwright
  # binary that would breach GitHub's 100MB per-file hard limit.
  --exclude='*_env'
  --exclude='site-packages'
  --exclude='*.so'
  --exclude='*.abi3.so'
  # secrets
  --exclude='.env'
  --exclude='.env.*'
  --exclude='*.pem'
  --exclude='*.key'
  --exclude='credentials'
  --exclude='*credentials*'
)

log() { printf '  %s\n' "$*"; }

# --- 1. Agent personas + memory (IRREPLACEABLE) -----------------------------
log "[1/4] Agent personas and memory..."
mkdir -p "${BUNDLE}/agents"
for ws in /root/agents/*/workspace; do
  agent="$(basename "$(dirname "${ws}")")"
  dest="${BUNDLE}/agents/${agent}"
  mkdir -p "${dest}"
  # Persona files define who each agent is. Memory files are their accumulated context.
  for f in SOUL IDENTITY USER AGENTS MEMORY TOOLS HEARTBEAT; do
    [ -f "${ws}/${f}.md" ] && cp "${ws}/${f}.md" "${dest}/" || true
  done
  [ -d "${ws}/memory" ]  && cp -r "${ws}/memory"  "${dest}/" 2>/dev/null || true
  [ -d "${ws}/skills" ]  && tar cf - "${EXCLUDES[@]}" -C "${ws}" skills 2>/dev/null | tar xf - -C "${dest}" || true
  [ -d "${ws}/scripts" ] && tar cf - "${EXCLUDES[@]}" -C "${ws}" scripts 2>/dev/null | tar xf - -C "${dest}" || true
  [ -d "${ws}/inbox" ]   && cp -r "${ws}/inbox" "${dest}/" 2>/dev/null || true
done

# --- 2. Un-backed-up openclaw workspaces ------------------------------------
# These have NO git remote — if this box dies, they are gone. Highest priority.
log "[2/4] Orphan workspaces (no git remote)..."
mkdir -p "${BUNDLE}/openclaw-workspaces"
for ws in /root/.openclaw/workspace /root/.openclaw/workspace-*; do
  [ -d "${ws}" ] || continue
  # Skip anything that already has a remote — it lives on GitHub already.
  if git -C "${ws}" remote get-url origin >/dev/null 2>&1; then
    log "      skip $(basename "${ws}") (has remote)"
    continue
  fi
  tar cf - "${EXCLUDES[@]}" -C /root/.openclaw "$(basename "${ws}")" 2>/dev/null \
    | tar xf - -C "${BUNDLE}/openclaw-workspaces" || true
done

# --- 3. System configuration -------------------------------------------------
log "[3/4] System config (sanitized)..."
mkdir -p "${BUNDLE}/system"
crontab -l > "${BUNDLE}/system/crontab.txt" 2>/dev/null || true
cp /root/agents/bin/run-agent.sh "${BUNDLE}/system/" 2>/dev/null || true
cp /root/agents/agent-configs.json "${BUNDLE}/system/" 2>/dev/null || true

# Strip every secret-shaped value out of the runtime config before it is stored.
python3 - "${BUNDLE}/system" <<'PY'
import json, re, sys, pathlib
out = pathlib.Path(sys.argv[1])
SECRET_HINT = re.compile(r'(token|key|secret|password|passwd|credential|apiKey)', re.I)
SECRET_VALUE = re.compile(r'^(ghp_|github_pat_|sk-|sk_|xox[baprs]-|AIza|eyJ)')

def scrub(node):
    if isinstance(node, dict):
        return {k: ("<REDACTED>" if (SECRET_HINT.search(k) and isinstance(v, str) and v)
                    else scrub(v)) for k, v in node.items()}
    if isinstance(node, list):
        return [scrub(v) for v in node]
    if isinstance(node, str) and SECRET_VALUE.match(node):
        return "<REDACTED>"
    return node

for src, name in [("/root/.openclaw/openclaw.json", "openclaw.sanitized.json"),
                  ("/root/agents/telegram-bots.json", "telegram-bots.sanitized.json")]:
    try:
        (out / name).write_text(json.dumps(scrub(json.load(open(src))), indent=2))
    except Exception as e:
        (out / name).write_text(f"// could not sanitize {src}: {e}\n")
PY

# --- 3a. Redact secrets embedded in file CONTENTS ----------------------------
# Excluding .env files is not sufficient: live tokens are pasted inside agent
# memory logs, TOOLS.md notes, and scripts. Those files must be kept (they are
# the irreplaceable part of this backup), so scrub the values instead.
log "[3a] Redacting embedded secrets..."
python3 - "${BUNDLE}" <<'PY'
import re, sys, pathlib

bundle = pathlib.Path(sys.argv[1])
PATTERNS = [
    (re.compile(r'gh[pousr]_[A-Za-z0-9]{36,}'),                  'GITHUB_PAT'),
    (re.compile(r'github_pat_[A-Za-z0-9_]{50,}'),                'GITHUB_PAT'),
    # No \b anchors: these tokens are usually embedded in a Telegram API URL
    # (".../bot<TOKEN>/sendMessage"), and "t"->digit is not a word boundary,
    # so a leading \b silently fails to match exactly where it matters most.
    (re.compile(r'\d{8,12}:AA[A-Za-z0-9_-]{32,36}'),             'TELEGRAM_BOT_TOKEN'),
    (re.compile(r'\bsk-[A-Za-z0-9._-]{20,}'),                    'API_KEY'),
    (re.compile(r'\bsk_[A-Za-z0-9._-]{20,}'),                    'API_KEY'),
    (re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{10,}'),              'SLACK_TOKEN'),
    (re.compile(r'\bAIza[A-Za-z0-9_-]{35}\b'),                   'GOOGLE_API_KEY'),
    (re.compile(r'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}'), 'JWT'),
]
TEXT_SUFFIX = {'.md', '.txt', '.py', '.js', '.mjs', '.sh', '.json', '.yml',
               '.yaml', '.env', '.sql', '.html', '.css', '.cfg', '.ini', '.toml'}

changed = total = 0
for path in bundle.rglob('*'):
    if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIX:
        continue
    try:
        original = path.read_text(encoding='utf-8', errors='surrogateescape')
    except Exception:
        continue
    redacted, hits = original, 0
    for pattern, label in PATTERNS:
        redacted, n = pattern.subn(f'<REDACTED:{label}>', redacted)
        hits += n
    if hits:
        path.write_text(redacted, encoding='utf-8', errors='surrogateescape')
        changed += 1
        total += hits

print(f"      redacted {total} secret(s) across {changed} file(s)")
PY

# --- 3b. Enforce per-file size cap ------------------------------------------
# GitHub hard-rejects any file >100MB. Cap at 50MB for headroom, and record
# every dropped file so the backup never silently under-reports coverage.
readonly MAX_FILE_MB=50
DROPPED="${BUNDLE}/DROPPED.txt"
{
  echo "Files omitted from this backup (larger than ${MAX_FILE_MB}MB)."
  echo "These are NOT backed up. Re-download or regenerate them if needed."
  echo
} > "${DROPPED}"

find "${BUNDLE}" -type f -size +$((MAX_FILE_MB * 1024))k -print0 2>/dev/null \
  | while IFS= read -r -d '' big; do
      printf '  %8sMB  %s\n' \
        "$(( $(stat -c%s "$big") / 1048576 ))" "${big#"${BUNDLE}"/}" >> "${DROPPED}"
      rm -f "$big"
    done

if [ "$(wc -l < "${DROPPED}")" -gt 3 ]; then
  log "      dropped oversized files — see DROPPED.txt"
fi

# --- 4. Manifest -------------------------------------------------------------
log "[4/4] Manifest..."
{
  echo "THHT Fleet Backup — ${STAMP}"
  echo "Generated by scripts/backup-all.sh"
  echo
  echo "SECRETS ARE EXCLUDED. See RECOVERY.md for where to re-supply them."
  echo
  echo "== Contents =="
  du -sh "${BUNDLE}"/* 2>/dev/null | sed 's|'"${BUNDLE}"'/|  |'
  echo
  echo "== File count =="
  find "${BUNDLE}" -type f | wc -l
} > "${BUNDLE}/MANIFEST.txt"

cp /root/agents/ryan-chen/workspace/RECOVERY.md "${BUNDLE}/" 2>/dev/null || true

tar czf "${ARCHIVE}" -C "${STAGE}" "thht-backup-${STAMP}"

# --- Safety net: fail loudly if a secret slipped through ---------------------
# Checks both filenames AND file contents. A filename-only check gives a false
# all-clear, because most leaked tokens here are pasted inside .md and .py files.
if tar tzf "${ARCHIVE}" | grep -qE '(^|/)\.env$|\.pem$|credentials/'; then
  echo "ERROR: secret-shaped FILE found in archive — aborting." >&2
  rm -f "${ARCHIVE}"; exit 1
fi

SECRET_RE='gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{50}|[0-9]{8,12}:AA[A-Za-z0-9_-]{32}|sk[-_][A-Za-z0-9._-]{20}|xox[baprs]-[A-Za-z0-9-]{10}|AIza[A-Za-z0-9_-]{35}'
if tar xzf "${ARCHIVE}" -O 2>/dev/null | grep -qEa "${SECRET_RE}"; then
  echo "ERROR: secret VALUE found inside archive contents — aborting." >&2
  rm -f "${ARCHIVE}"; exit 1
fi
echo "  Secret scan: clean (filenames + contents)"

echo
echo "Archive: ${ARCHIVE} ($(du -h "${ARCHIVE}" | cut -f1))"
