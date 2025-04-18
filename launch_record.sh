progs=$(jq -r '.[] | @base64' "$HOME/.local/share/tvselect-fr/info_progs.json")

cd $HOME/videos_select

for row in $progs;
do
    _jq() {
     echo ${row} | base64 --decode | jq -r ${1}
    }
    echo "tzap -t $(_jq '.duration') -o $(_jq '.title') \"$(_jq '.channel')\" >> $HOME/.local/share/tvselect-fr/logs/cron_launch_record.log 2>&1" | at $(_jq '.start')
done
