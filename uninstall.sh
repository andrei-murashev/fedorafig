#!/bin/bash

trap 'exit' INT

rm -rf ~/.config/fedorafig/ || true
rm -rf ~/.local/state/fedorafig/ ~/.local/lib/fedorafig/ || true
rm ~/.local/bin/fedorafig || true
