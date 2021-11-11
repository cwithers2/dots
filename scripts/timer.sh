#!/usr/bin/env bash

WORKDIR="/tmp"
FILE_NAME="timer"
PROGRAM_NAME="Timer"

COMMON_INPUTS="clear
1 minute
5 minutes
10 minutes
25 minutes
30 minutes
1 hour
"
TIME_FMT="%l:%M %P"
ICON_NAME="time-admin"

cd $WORKDIR

menu() {
	input="$(printf "$COMMON_INPUTS" | rofi -dmenu -mesg "Set timer:" -theme themes/timer)"
	#exit on conditions the main program might not expect
	if [ "$?" -ne 0 ] || [ "$input" = "" ]; then
		return 1
	fi
	echo $input
}

notify() {
	level=$1; shift
	notify-send "$PROGRAM_NAME" "$*" -u $level -i $ICON_NAME
}

start_timer() {
	timeout=$(($1 - $(date --date=now +%s)))
	printf "$1" > "$FILE_NAME"
	inotifywait -t $timeout -e delete_self "$FILE_NAME"
	if [ $? -eq 0 ]; then #someone deleted us, bail
		return 1
	else # we timedout as planned
		rm "$FILE_NAME"
		return 0
	fi
}

kill_timer() {
	rm "$FILE_NAME"
}

clocktime() {
	date --date="$*" +"$TIME_FMT"
}

input="$(menu)" || exit 0

if [ "$input" = "clear" ]; then
	kill_timer
	exit 0
fi

#we have the input to set a timer, but a timer could already exist
if [ -f "$FILE_NAME" ]; then
	timestamp=$(cat "$FILE_NAME")
	if [ "$timestamp" -ge $(date --date="now" +%s) ]; then
		notify critical "Timer already set for $(clocktime @$timestamp)."
		exit 1
	else
		#the timer is expired
		echo "WARNING: timer artifact found." 1>&2
		kill_timer
	fi
fi

#use some commandline magic to transform input into unix timestamp
timestamp=$(date --date="now + $input" +%s 2>&1)
if [ $? -ne 0 ]; then
	notify critical $timestamp
	exit 1
fi

notify low "Timer set for $(clocktime @$timestamp)."
trap kill_timer EXIT #do our best to make sure the file lock is gone when we leave.

start_timer $timestamp
if [ $? -eq 0 ]; then
	notify normal "Time's up!"
else
	notify low "Timer cleared."
fi
