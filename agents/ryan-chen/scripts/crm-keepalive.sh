#!/bin/bash

# CRM Keep-Alive Monitor
# Checks clientlist.onrender.com and thht-hq.onrender.com health
# Logs errors and alerts if endpoints are down

ENDPOINTS=(
  "https://clientlist.onrender.com"
  "https://thht-hq.onrender.com"
)

LOG_FILE="/root/agents/ryan-chen/workspace/logs/crm-keepalive.log"

mkdir -p "$(dirname "$LOG_FILE")"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
ERRORS=()

for endpoint in "${ENDPOINTS[@]}"; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$endpoint")

  if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "301" ] && [ "$HTTP_CODE" != "302" ]; then
    ERRORS+=("$endpoint returned HTTP $HTTP_CODE")
    echo "[$TIMESTAMP] ERROR: $endpoint returned HTTP $HTTP_CODE" >> "$LOG_FILE"
  else
    echo "[$TIMESTAMP] OK: $endpoint (HTTP $HTTP_CODE)" >> "$LOG_FILE"
  fi
done

# Alert if there are errors
if [ ${#ERRORS[@]} -gt 0 ]; then
  ALERT_MSG="[$TIMESTAMP] CRM KEEP-ALIVE ALERT: ${#ERRORS[@]} endpoint(s) down"
  echo "$ALERT_MSG" >> "$LOG_FILE"
  for err in "${ERRORS[@]}"; do
    echo "  - $err" >> "$LOG_FILE"
  done
  exit 1
else
  exit 0
fi
