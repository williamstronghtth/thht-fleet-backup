#!/bin/bash
# Full season backtest: 2025-10-21 through 2026-03-15
cd /Users/cuzifelt1ikeit/.openclaw/workspace-coding/projects/papernba
source .venv/bin/activate

RESULTS_FILE="backtest_results.log"
echo "BACKTEST START: $(date)" > "$RESULTS_FILE"

total_days=0
total_picks=0
total_wins=0
total_losses=0
error_dates=""

# Generate all dates from 2025-10-21 to 2026-03-15
current="2025-10-21"
end="2026-03-15"

while [[ "$current" < "$end" ]] || [[ "$current" == "$end" ]]; do
    total_days=$((total_days + 1))
    
    # Run backtest for this date with retry logic
    max_retries=3
    attempt=0
    success=false
    
    while [[ $attempt -lt $max_retries ]]; do
        attempt=$((attempt + 1))
        output=$(python3 backtest_day.py "$current" 2>&1)
        exit_code=$?
        
        echo "[$current] attempt=$attempt exit=$exit_code" >> "$RESULTS_FILE"
        echo "$output" >> "$RESULTS_FILE"
        
        # Check for rate limit (429)
        if echo "$output" | grep -qi "429\|rate.limit\|quota.*exceed\|RESOURCE_EXHAUSTED"; then
            echo "[$current] Rate limited, waiting 65s before retry..." >> "$RESULTS_FILE"
            sleep 65
            continue
        fi
        
        # Check for other errors
        if [[ $exit_code -ne 0 ]]; then
            echo "[$current] Error (exit=$exit_code), waiting 10s before retry..." >> "$RESULTS_FILE"
            sleep 10
            continue
        fi
        
        success=true
        break
    done
    
    if [[ "$success" != "true" ]]; then
        error_dates="$error_dates $current"
        echo "[$current] FAILED after $max_retries attempts" >> "$RESULTS_FILE"
    fi
    
    # Parse picks/wins from output
    if echo "$output" | grep -q "picks:"; then
        picks_line=$(echo "$output" | grep "picks:")
        day_picks=$(echo "$picks_line" | grep -oP '\d+(?= picks)')
        day_wins=$(echo "$picks_line" | grep -oP '\d+(?=W)')
        day_losses=$(echo "$picks_line" | grep -oP '(?<=W-)\d+')
        total_picks=$((total_picks + ${day_picks:-0}))
        total_wins=$((total_wins + ${day_wins:-0}))
        total_losses=$((total_losses + ${day_losses:-0}))
        echo "  PICKS: ${day_picks:-0} W:${day_wins:-0} L:${day_losses:-0}" >> "$RESULTS_FILE"
    fi
    
    # Progress every 10 days
    if [[ $((total_days % 10)) -eq 0 ]]; then
        echo "PROGRESS: $total_days days done, $total_picks picks ($total_wins-$total_losses), date=$current" >> "$RESULTS_FILE"
    fi
    
    # Rate limit protection - 3 second sleep between days
    sleep 3
    
    # Next date
    current=$(date -j -v+1d -f "%Y-%m-%d" "$current" "+%Y-%m-%d" 2>/dev/null || python3 -c "from datetime import date,timedelta; print(date.fromisoformat('$current')+timedelta(1))")
done

echo "" >> "$RESULTS_FILE"
echo "===== FINAL SUMMARY =====" >> "$RESULTS_FILE"
echo "Total days: $total_days" >> "$RESULTS_FILE"
echo "Total picks: $total_picks" >> "$RESULTS_FILE"
echo "Record: ${total_wins}W-${total_losses}L" >> "$RESULTS_FILE"
echo "Error dates: ${error_dates:-none}" >> "$RESULTS_FILE"
echo "BACKTEST END: $(date)" >> "$RESULTS_FILE"

# Output summary for parsing
echo "SUMMARY|$total_days|$total_picks|$total_wins|$total_losses|${error_dates:-none}"
