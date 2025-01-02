#!/bin/bash


source <(python3 src/cmn.py)
echo "$CFG_DIR"
echo "$PROG_DIR"
echo "$EXEC_DIR"
echo "$STATE_DIR"

set -e
mkdir -p "$CFG_DIR" "$PROG_DIR" "$EXEC_DIR" "$STATE_DIR"
chown "$USER":"$USER" -R "$CFG_DIR" "$PROG_DIR" "$EXEC_DIR" "$STATE_DIR"
chmod u+x src/main.py
cp -rf src/. "$PROG_DIR"
ln -s "$PROG_DIR"/main.py "$EXEC_DIR"/fedorafig
