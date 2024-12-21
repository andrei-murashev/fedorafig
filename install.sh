#!/bin/bash

trap 'exit' INT

source <(python3 src/cfg.py)
mkdir -p "$CFG_DIR" "$PROG_DIR" "$EXEC_DIR" "$STATE_DIR"
chmod u+x src/main.py
cp -rf src/. "$PROG_DIR"
ln -s "$PROG_DIR"/main.py "$EXEC_DIR"/fedorafig
