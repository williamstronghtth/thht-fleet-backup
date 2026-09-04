#!/usr/bin/env bash
set -euo pipefail

# Load shared secrets so agent scripts (e.g. Jack's email campaigns) can read
# credentials from the environment instead of hardcoding them. Cron already
# sources this, but non-cron invocations (Telegram, manual) did not — without
# it, os.environ["JACK_EMAIL_APP_PASSWORD"] would raise KeyError.
if [[ -f /root/agents/.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source /root/agents/.env
  set +a
fi

# --- Usage & Argument Parsing ---
usage() {
  echo "Usage: $0 <agent-id> <task-message> [--telegram] [--max-turns N] [--model haiku|sonnet|opus] [--cleanup] [--cleanup-fix] [--full-context] [--tier N]"
  exit 1
}

[[ $# -lt 2 ]] && usage

AGENT_ID="$1"
TASK_MESSAGE="$2"
shift 2

SEND_TELEGRAM=false
MAX_TURNS=90
MODEL_OVERRIDE=""
RUN_CLEANUP=false
CLEANUP_FIX=false
FULL_CONTEXT=false
FORCED_TIER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --telegram) SEND_TELEGRAM=true; shift ;;
    --max-turns) MAX_TURNS="$2"; shift 2 ;;
    --model) MODEL_OVERRIDE="$2"; shift 2 ;;
    --cleanup) RUN_CLEANUP=true; shift ;;
    --cleanup-fix) RUN_CLEANUP=true; CLEANUP_FIX=true; shift ;;
    --full-context) FULL_CONTEXT=true; shift ;;
    --tier) FORCED_TIER="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

# --- Constants ---
AGENTS_ROOT="$HOME/agents"
TELEGRAM_CHAT_ID="8560812913"
TODAY=$(TZ=America/New_York date +%Y-%m-%d)
YESTERDAY=$(TZ=America/New_York date -d "yesterday" +%Y-%m-%d)

# --- Workspace ---
if [[ "$AGENT_ID" == "main" ]]; then
  WORKSPACE="$AGENTS_ROOT/william-strong/workspace"
else
  WORKSPACE="$AGENTS_ROOT/$AGENT_ID/workspace"
fi

if [[ ! -d "$WORKSPACE" ]]; then
  echo "Error: workspace not found: $WORKSPACE" >&2
  exit 1
fi

# --- Log Setup ---
LOG_DIR="$AGENTS_ROOT/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/${AGENT_ID}_${TODAY}.log"

log() {
  echo "[$(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

log "Starting agent '$AGENT_ID' with max_turns=$MAX_TURNS telegram=$SEND_TELEGRAM"

# --- Context Resolution (Dispatch phase) ---
build_system_prompt() {
  local CONTEXT_TIER="$1"
  local SYSTEM_PROMPT=""

  # Resolve which files to include
  local RESOLVER_ARGS="$AGENT_ID"
  RESOLVER_ARGS+=" '$TASK_MESSAGE'"

  local CONTEXT_FILES
  if [[ "$FULL_CONTEXT" == true ]]; then
    CONTEXT_FILES=$(python3 "$AGENTS_ROOT/bin/context-resolver.py" "$AGENT_ID" "$TASK_MESSAGE" --tier 4)
    log "Context: full (forced)"
  elif [[ -n "$FORCED_TIER" ]]; then
    CONTEXT_FILES=$(python3 "$AGENTS_ROOT/bin/context-resolver.py" "$AGENT_ID" "$TASK_MESSAGE" --tier "$FORCED_TIER")
    log "Context: tier $FORCED_TIER (forced)"
  elif [[ -n "$CONTEXT_TIER" ]]; then
    CONTEXT_FILES=$(python3 "$AGENTS_ROOT/bin/context-resolver.py" "$AGENT_ID" "$TASK_MESSAGE" --tier "$CONTEXT_TIER")
    log "Context: tier $CONTEXT_TIER (retry escalation)"
  else
    CONTEXT_FILES=$(python3 "$AGENTS_ROOT/bin/context-resolver.py" "$AGENT_ID" "$TASK_MESSAGE")
    log "Context: auto-resolved"
  fi

  # Log the classification
  local CLASSIFICATION
  CLASSIFICATION=$(python3 "$AGENTS_ROOT/bin/context-resolver.py" "$AGENT_ID" "$TASK_MESSAGE" --list-tiers 2>/dev/null || true)
  log "Classification: $CLASSIFICATION"

  # Helper: check if a file/virtual entry is in the resolved list
  has_context() {
    echo "$CONTEXT_FILES" | grep -qx "$1"
  }

  # --- Identity Files ---
  for file in SOUL.md IDENTITY.md USER.md MISSION.md STRATEGY.md TRADING_RULES.md AGENTS.md TOOLS.md HEARTBEAT.md; do
    if has_context "$file" && [[ -f "$WORKSPACE/$file" ]]; then
      SYSTEM_PROMPT+=$'\n'"$(cat "$WORKSPACE/$file")"$'\n'
    fi
  done

  # --- Memory ---
  if has_context "MEMORY.md" && [[ -f "$WORKSPACE/MEMORY.md" ]]; then
    SYSTEM_PROMPT+=$'\n--- LONG-TERM MEMORY ---\n'
    SYSTEM_PROMPT+="$(cat "$WORKSPACE/MEMORY.md")"$'\n'
  fi

  if has_context "today_memory" && [[ -f "$WORKSPACE/memory/$TODAY.md" ]]; then
    SYSTEM_PROMPT+=$'\n--- MEMORY: '"$TODAY"$' ---\n'
    SYSTEM_PROMPT+="$(cat "$WORKSPACE/memory/$TODAY.md")"$'\n'
  fi

  if has_context "yesterday_memory" && [[ -f "$WORKSPACE/memory/$YESTERDAY.md" ]]; then
    SYSTEM_PROMPT+=$'\n--- MEMORY: '"$YESTERDAY"$' ---\n'
    SYSTEM_PROMPT+="$(cat "$WORKSPACE/memory/$YESTERDAY.md")"$'\n'
  fi

  # --- Inbox ---
  if has_context "inbox"; then
    INBOX_DIR="$WORKSPACE/inbox"
    if [[ -d "$INBOX_DIR" ]]; then
      inbox_files=()
      while IFS= read -r -d '' f; do
        inbox_files+=("$f")
      done < <(find "$INBOX_DIR" -maxdepth 1 -name '*.md' -print0 2>/dev/null)

      if [[ ${#inbox_files[@]} -gt 0 ]]; then
        SYSTEM_PROMPT+=$'\n--- INBOX ---\n'
        for f in "${inbox_files[@]}"; do
          SYSTEM_PROMPT+=$'\n## '"$(basename "$f")"$'\n'
          SYSTEM_PROMPT+="$(cat "$f")"$'\n'
        done

        mkdir -p "$INBOX_DIR/processed"
        for f in "${inbox_files[@]}"; do
          mv "$f" "$INBOX_DIR/processed/"
        done
        log "Processed ${#inbox_files[@]} inbox message(s)"
      fi
    fi
  fi

  # --- Session Log ---
  if has_context "session_log"; then
    RECENT_LOG_FILE="$LOG_DIR/${AGENT_ID}_${TODAY}.log"
    if [[ -f "$RECENT_LOG_FILE" && -s "$RECENT_LOG_FILE" ]]; then
      RECENT_LOG_TAIL=$(tail -c 2000 "$RECENT_LOG_FILE")
      SYSTEM_PROMPT+=$'\n--- RECENT SESSION LOG ---\n'
      SYSTEM_PROMPT+="Below is the tail of your session log from today. Use it to maintain continuity with previous messages."$'\n'
      SYSTEM_PROMPT+="$RECENT_LOG_TAIL"$'\n'
    fi
  fi

  # --- Runtime Context (always included) ---
  if has_context "runtime"; then
    SYSTEM_PROMPT+=$'\n--- RUNTIME CONTEXT ---\n'
    SYSTEM_PROMPT+="Current date/time (ET): $(TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z')"$'\n'
    SYSTEM_PROMPT+="Timezone: America/New_York"$'\n'
    SYSTEM_PROMPT+="Agent ID: $AGENT_ID"$'\n'
    SYSTEM_PROMPT+="Workspace: $WORKSPACE"$'\n'
  fi

  # --- Telegram ---
  if has_context "telegram"; then
    SYSTEM_PROMPT+=$'\n--- TELEGRAM ---\n'
    SYSTEM_PROMPT+='To send Chris a Telegram message, use this command:'
    SYSTEM_PROMPT+=$'\n'
    BOT_TOKEN=$(python3 -c "import json; bots=json.load(open('/root/agents/telegram-bots.json'))['bots']; print(next(b['bot_token'] for b in bots if b['agent_id']=='$AGENT_ID'))")
    SYSTEM_PROMPT+='```bash'$'\n'
    SYSTEM_PROMPT+="curl -s -X POST \"https://api.telegram.org/bot${BOT_TOKEN}/sendMessage\" \\"$'\n'
    SYSTEM_PROMPT+='  -d chat_id="8560812913" \'$'\n'
    SYSTEM_PROMPT+='  -d text="YOUR MESSAGE" \'$'\n'
    SYSTEM_PROMPT+='  -d parse_mode="Markdown"'$'\n'
    SYSTEM_PROMPT+='```'$'\n'
  fi

  SYSTEM_PROMPT+=$'\n## Memory\n'
  SYSTEM_PROMPT+="Write notes and observations to: $WORKSPACE/memory/$TODAY.md"$'\n'
  SYSTEM_PROMPT+="Append to this file throughout your session to persist learnings."$'\n'

  SYSTEM_PROMPT+=$'\n## Response Protocol\n'
  SYSTEM_PROMPT+="CRITICAL: You MUST always end with a visible text response to the user. NEVER finish with only tool calls."$'\n'
  SYSTEM_PROMPT+="After performing any actions (file edits, bash commands, etc.), always include a brief text summary of what you did."$'\n'
  SYSTEM_PROMPT+="If you have nothing to do, still respond with a short acknowledgment. Empty responses are not acceptable."$'\n'

  SYSTEM_PROMPT+=$'\n## Session End Protocol\n'
  SYSTEM_PROMPT+="IMPORTANT: Before you finish your final response, you MUST append a session summary to your memory file."$'\n'
  SYSTEM_PROMPT+="File: $WORKSPACE/memory/$TODAY.md"$'\n'
  SYSTEM_PROMPT+='Format (append, do not overwrite):'$'\n'
  SYSTEM_PROMPT+='```'$'\n'
  SYSTEM_PROMPT+='## Session — <HH:MM ET>'$'\n'
  SYSTEM_PROMPT+='- **What was done:** (bullet points of key actions/changes)'$'\n'
  SYSTEM_PROMPT+='- **Key decisions:** (any important choices and why)'$'\n'
  SYSTEM_PROMPT+='- **Open items:** (anything unfinished or needs follow-up)'$'\n'
  SYSTEM_PROMPT+='- **Files changed:** (list of files created/modified)'$'\n'
  SYSTEM_PROMPT+='```'$'\n'
  SYSTEM_PROMPT+="Keep it to 10-15 lines max. This is your future self's only record of this session."$'\n'

  SYSTEM_PROMPT+=$'\n## Inter-Agent Messaging\n'
  SYSTEM_PROMPT+="To call another agent and get an immediate response in this session, run:"$'\n'
  SYSTEM_PROMPT+='```bash'$'\n'
  SYSTEM_PROMPT+="bash /root/agents/bin/run-agent.sh <agent-id> 'your message here'"$'\n'
  SYSTEM_PROMPT+='```'$'\n'
  SYSTEM_PROMPT+=$'\n'
  SYSTEM_PROMPT+="This runs the other agent and returns their response directly. You can then relay it to Chris or act on it."$'\n'
  SYSTEM_PROMPT+=$'\n'
  SYSTEM_PROMPT+="Available agent IDs: main, ryan-chen, jack-sullivan, fiona-murphy, derek-marshall, arthur-pembroke, nolan-price, calvin-king, elliot-crane, eno-sarris, oliver-kensington, willow-hayes, iris-vale, miles-redgrave."$'\n'
  SYSTEM_PROMPT+=$'\n'
  SYSTEM_PROMPT+="For async messages where you do not need an immediate response, write a .md file to /root/agents/<agent-id>/workspace/inbox/"$'\n'

  echo "$SYSTEM_PROMPT"
}

# --- Write System Prompt to Temp File ---
TMPFILE=$(mktemp /tmp/agent-system-prompt.XXXXXX)
cleanup() {
  rm -f "$TMPFILE"
}
trap cleanup EXIT

# --- Model Routing ---
if [[ -n "$MODEL_OVERRIDE" ]]; then
  MODEL="$MODEL_OVERRIDE"
  log "Model override: $MODEL"
else
  MODEL=$(python3 "$AGENTS_ROOT/bin/resolve-model.py" "$AGENT_ID" "$TASK_MESSAGE" 2>/dev/null || echo "sonnet")
  log "Model auto-routed: $MODEL"
fi

# --- Run Claude with Iterative Context (Dispatch → Evaluate → Refine → Loop) ---
MAX_CONTEXT_RETRIES=1
CONTEXT_RETRY=0
CURRENT_TIER=""
OUTPUT=""
EXIT_CODE=0

while true; do
  # Dispatch: build system prompt with current tier
  BUILT_PROMPT=$(build_system_prompt "$CURRENT_TIER")
  echo "$BUILT_PROMPT" > "$TMPFILE"

  PROMPT_SIZE=$(wc -c < "$TMPFILE")
  log "System prompt size: ${PROMPT_SIZE}B (retry=$CONTEXT_RETRY)"

  # Evaluate: run the agent
  log "Running claude in $WORKSPACE with model=$MODEL"

  set +e
  TASK_FILE=$(mktemp /tmp/agent-task.XXXXXX)
  printf '%s\n\nIMPORTANT: After completing the task above, you MUST end with a visible text reply (not just tool calls). Summarize what you did in 1-3 sentences. If you have nothing to do, acknowledge briefly. Empty responses are not acceptable.' "$TASK_MESSAGE" > "$TASK_FILE"
  OUTPUT=$(cd "$WORKSPACE" && cat "$TASK_FILE" | claude -p - \
    --model "$MODEL" \
    --max-turns "$MAX_TURNS" \
    --system-prompt-file "$TMPFILE" \
    --allowedTools "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch" 2>&1)
  EXIT_CODE=$?
  rm -f "$TASK_FILE"
  set -e

  # Fallback: if output is empty, retry once then provide a descriptive response
  if [[ -z "$OUTPUT" || "$OUTPUT" =~ ^[[:space:]]*$ ]]; then
    log "Empty output detected (exit=$EXIT_CODE), retrying once"
    RETRY_TASK_FILE=$(mktemp /tmp/agent-retry.XXXXXX)
    printf '%s\n\nIMPORTANT: You MUST respond with a visible text summary. Describe what you did or what happened. Never return an empty response.' "$TASK_MESSAGE" > "$RETRY_TASK_FILE"
    set +e
    OUTPUT=$(cd "$WORKSPACE" && cat "$RETRY_TASK_FILE" | claude -p - \
      --model "$MODEL" \
      --max-turns "$MAX_TURNS" \
      --system-prompt-file "$TMPFILE" \
      --allowedTools "Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch" 2>&1)
    set -e
    rm -f "$RETRY_TASK_FILE"

    # If still empty after retry, build a meaningful fallback from the task
    if [[ -z "$OUTPUT" || "$OUTPUT" =~ ^[[:space:]]*$ ]]; then
      TASK_PREVIEW="${TASK_MESSAGE:0:200}"
      OUTPUT="⚠️ Task ran but returned no output. Task was: \"${TASK_PREVIEW}\". Check logs at $LOG_FILE for details."
      log "Empty output after retry, using descriptive fallback"
    else
      log "Retry succeeded — got non-empty output"
    fi
  fi

  log "Claude exited with code $EXIT_CODE"
  echo "$OUTPUT" >> "$LOG_FILE"

  # Refine + Loop: check if agent needs more context
  if [[ "$FULL_CONTEXT" == true || -n "$FORCED_TIER" ]]; then
    break  # no retry when context was explicitly set
  fi

  if [[ $CONTEXT_RETRY -ge $MAX_CONTEXT_RETRIES ]]; then
    break  # max retries reached
  fi

  # Check output for missing-context signals
  NEEDS_MORE=$(python3 "$AGENTS_ROOT/bin/context-resolver.py" "$AGENT_ID" "$TASK_MESSAGE" \
    --check-output "$OUTPUT" 2>/dev/null && echo "no" || echo "yes")

  if [[ "$NEEDS_MORE" == "yes" ]]; then
    # Escalate to full context and retry
    CURRENT_TIER="4"
    CONTEXT_RETRY=$((CONTEXT_RETRY + 1))
    log "Context escalation: agent signaled missing context, retrying with tier 4 (attempt $CONTEXT_RETRY)"
  else
    break  # agent had enough context
  fi
done

# --- Telegram ---
if [[ "$SEND_TELEGRAM" == true ]]; then
  log "Sending output to Telegram"

  BOT_TOKEN=$(python3 -c "import json; bots=json.load(open('/root/agents/telegram-bots.json'))['bots']; print(next(b['bot_token'] for b in bots if b['agent_id']=='$AGENT_ID'))")

  # Truncate to 4000 chars if needed
  TELEGRAM_TEXT="$OUTPUT"
  if [[ ${#TELEGRAM_TEXT} -gt 4000 ]]; then
    TELEGRAM_TEXT="${TELEGRAM_TEXT:0:3997}..."
  fi

  # Try with Markdown parse_mode first
  RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
    -d chat_id="$TELEGRAM_CHAT_ID" \
    --data-urlencode text="$TELEGRAM_TEXT" \
    -d parse_mode="Markdown" 2>&1) || true

  # Check if it succeeded
  OK=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ok', False))" 2>/dev/null || echo "False")

  if [[ "$OK" != "True" ]]; then
    log "Markdown send failed, retrying without parse_mode"
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
      -d chat_id="$TELEGRAM_CHAT_ID" \
      --data-urlencode text="$TELEGRAM_TEXT" > /dev/null 2>&1 || log "Telegram send failed"
  fi

  log "Telegram message sent"
fi

# --- Cleanup Pass ---
if [[ "$RUN_CLEANUP" == true ]]; then
  log "Running cleanup pass"
  CLEANUP_ARGS="$AGENT_ID"
  [[ "$CLEANUP_FIX" == true ]] && CLEANUP_ARGS+=" --fix"
  CLEANUP_OUTPUT=$("$AGENTS_ROOT/bin/cleanup-pass.sh" $CLEANUP_ARGS 2>&1) || true
  log "Cleanup output: $CLEANUP_OUTPUT"

  if [[ "$SEND_TELEGRAM" == true && -n "$CLEANUP_OUTPUT" ]]; then
    # Only send cleanup report if issues were found
    if echo "$CLEANUP_OUTPUT" | grep -qi "issues found: [1-9]"; then
      CLEANUP_TEXT="🧹 *Cleanup Report — $AGENT_ID*"$'\n'"$CLEANUP_OUTPUT"
      if [[ ${#CLEANUP_TEXT} -gt 4000 ]]; then
        CLEANUP_TEXT="${CLEANUP_TEXT:0:3997}..."
      fi
      curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d chat_id="$TELEGRAM_CHAT_ID" \
        --data-urlencode text="$CLEANUP_TEXT" > /dev/null 2>&1 || log "Cleanup Telegram send failed"
    fi
  fi
fi

# --- Output ---
echo "$OUTPUT"
