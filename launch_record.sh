#!/bin/bash
set -euo pipefail

JSON_FILE="$HOME/.local/share/tvselect-fr/info_progs.json"
LOG_FILE="$HOME/.local/share/tvselect-fr/logs/cron_launch_record.log"
VIDEO_DIR="$HOME/videos_select"
CHANNELS_CONF="$HOME/.local/share/tvselect-fr/channels.conf"

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
flock -n /tmp/dvbv5-zap.lock dvbv5-zap -t "$duration" -o "$title" -c "$CHANNELS_CONF" "$channel" >> "$LOG_FILE" 2>&1 || echo "\$(date): dvbv5-zap already running, skipping '$title'" >> "$LOG_FILE"
EOF

done
