#!/usr/bin/env bash
feh --bg-fill $HOME/Pictures/wallpaper*
conky -d -c $HOME/.config/conky/panel
$HOME/projects/wpanel/wpanel.py &
xsetroot -name "S O L A R I Z E D"
