#!/usr/bin/env sh
if [ "$1" = "pasystray" ]; then
	exit 0
fi

case $5 in
	"CRITICAL") sound=/usr/share/sounds/sound-icons/cockchafer-gentleman-1.wav ;;
	"LOW")      sound=/usr/share/sounds/sound-icons/percussion-50.wav ;;
	*)          sound=/usr/share/sounds/sound-icons/cembalo-1.wav ;;
esac
paplay $sound
