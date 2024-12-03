#!/bin/sh

mkdir -p ~/.config/fedorafig/ ~/.local/bin/
mkdir -p ~/.local/state/fedorafig/ ~/.local/lib/fedorafig
chmod u+x main.py
cp -rf . ~/.local/lib/fedorafig/
ln -s ~/.local/lib/fedorafig/main.py ~/.local/bin/fedorafig
