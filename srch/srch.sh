#!/usr/bin/env bash
cd $HOME/scripts/srch #workdir

KEYS="$(./srch_info.py --list)"

while true; do
    ENGINE="$(printf "$KEYS" | rofi -i -dmenu -theme themes/srch_engine)"
    [ $? -ne 0 ] && exit 0; #user exit
    KEY="$(printf "$KEYS"|grep "$ENGINE")"
    [ $? -ne 0 ] && exit 0; #user bad entry, goodbye!
    QUERY="$(rofi -mesg "Searching with $KEY" -dmenu -theme themes/srch_search)"
    [ $? -eq 0 ] && break; #user input given
done

URL="$(./srch_info.py --url "$KEY" "$QUERY")"
xdg-open "$URL"
