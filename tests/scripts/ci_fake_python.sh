#!/bin/sh
# Record installer calls and provide a fake virtual-environment executable.
printf '%s: %s\n' "$0" "$*" >>"$CALLS"
if [ "$1" = -m ] && [ "$2" = venv ]; then
	mkdir -p "$3/bin"
	cp "$0" "$3/bin/python"
fi
