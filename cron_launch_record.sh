echo --- crontab start: $(date) >> $HOME/.local/share/tvselect-fr/logs/cron_launch_record.log

bash launch_record.sh >> $HOME/.local/share/tvselect-fr/logs/cron_launch_record.log 2>&1

echo --- crontab end: $(date) >> $HOME/.local/share/tvselect-fr/logs/cron_launch_record.log
