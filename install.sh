#!/bin/sh

trap 'exit' INT

mkdir -p ~/.config/fedorafig/ ~/.local/bin/
mkdir -p ~/.local/state/fedorafig/ ~/.local/lib/fedorafig
chmod u+x src/main.py
cp -rf src/. ~/.local/lib/fedorafig/
ln -s ~/.local/lib/fedorafig/main.py ~/.local/bin/fedorafig
