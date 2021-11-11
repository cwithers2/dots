#!/usr/bin/env sh
#clone a git tree

WORK_DIR="$HOME/projects"
TITLE="git clone"

address="$(rofi -dmenu -mesg "Enter the URI of the tree to clone" -theme themes/git_clone)"
[ "$address" = "" ] && exit 0

mkdir -pv "$WORK_DIR"
cd "$WORK_DIR"

mode=critical
message="$(git clone $address 2>&1)"

if [ $? -eq 0 ]; then
	mode=normal
	message="Successfully cloned $address"
fi

notify-send "$TITLE" "$message" -i git -u $mode
