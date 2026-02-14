#!/bin/bash
set -euo pipefail

JSON_FILE="$HOME/.local/share/tvselect-fr/info_progs.json"
LOG_FILE="$HOME/.local/share/tvselect-fr/logs/cron_launch_record.log"
VIDEO_DIR="$HOME/videos_select"

mkdir -p "$(dirname "$LOG_FILE")"
cd "$VIDEO_DIR"

jq -c '.[]' "$JSON_FILE" | while read -r row; do

    duration=$(echo "$row" | jq -r '.duration')
    title=$(echo "$row" | jq -r '.title')
    channel=$(echo "$row" | jq -r '.channel')
    start=$(echo "$row" | jq -r '.start')

    # Basic validation
    [[ "$duration" =~ ^[0-9]+$ ]] || continue
    [[ "$start" =~ ^[0-9:[:space:]+-]+$ ]] || continue

    at "$start" <<EOF
tzap -t "$duration" -o "$title" "$channel" >> "$LOG_FILE" 2>&1
EOF

done
