#!/bin/bash

# CRM Keep-Alive Monitor
# Checks clientlist and thht-hq endpoints
# Alerts if either is down or returns error

ENDPOINTS=(
  "https://clientlist.onrender.com"
  "https://thht-hq.onrender.com"
)

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S ET")
ALERT_FILE="/root/agents/ryan-chen/workspace/logs/crm-alerts.log"
STATUS_FILE="/root/agents/ryan-chen/workspace/logs/crm-status.log"

# Ensure log directory exists
mkdir -p "$(dirname "$ALERT_FILE")"

# Initialize status
ERRORS=0
STATUS_MSG=""

# Check each endpoint
for endpoint in "${ENDPOINTS[@]}"; do
  response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$endpoint")

  if [ "$response" = "200" ] || [ "$response" = "301" ] || [ "$response" = "302" ]; then
    STATUS_MSG="$STATUS_MSG
✓ $endpoint: OK ($response)"
  else
    ERRORS=$((ERRORS + 1))
    STATUS_MSG="$STATUS_MSG
✗ $endpoint: ERROR (HTTP $response)"
    echo "[$TIMESTAMP] ALERT: $endpoint returned HTTP $response" >> "$ALERT_FILE"
  fi
done

# Log status
echo "[$TIMESTAMP]$STATUS_MSG" >> "$STATUS_FILE"

# Exit with error code if any endpoint failed
if [ $ERRORS -gt 0 ]; then
  echo "[$TIMESTAMP] ALERT: CRM Keep-Alive Check FAILED - $ERRORS endpoint(s) down" >> "$ALERT_FILE"
  exit 1
fi

exit 0
