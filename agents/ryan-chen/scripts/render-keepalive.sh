#!/bin/bash

# Render keep-alive monitor for CRM services
# Runs every 5 minutes to prevent free-tier spindown

ENDPOINT1="https://clientlist.onrender.com"
ENDPOINT2="https://thht-hq.onrender.com"
LOG_FILE="/root/agents/ryan-chen/workspace/logs/keepalive.log"

# Create log directory if needed
mkdir -p "$(dirname "$LOG_FILE")"

# Check both endpoints
RESPONSE1=$(curl -s -o /dev/null -w "%{http_code}" -m 10 "$ENDPOINT1")
RESPONSE2=$(curl -s -o /dev/null -w "%{http_code}" -m 10 "$ENDPOINT2")

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Log and alert if either fails
if [ "$RESPONSE1" != "200" ] || [ "$RESPONSE2" != "200" ]; then
  MSG="[$TIMESTAMP] ERROR: clientlist=$RESPONSE1, thht-hq=$RESPONSE2"
  echo "$MSG" >> "$LOG_FILE"
  echo "$MSG" >&2
  exit 1
else
  echo "[$TIMESTAMP] OK: clientlist=$RESPONSE1, thht-hq=$RESPONSE2" >> "$LOG_FILE"
  exit 0
fi
