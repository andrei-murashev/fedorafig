#!/bin/sh
rm -rf build/ || True; mkdir build/
pyinstaller src/main.py   \
  --upx-dir /usr/bin/upx  \
  --distpath build/dist   \
  --workpath build/build  \
  --specpath build/       \
  --name fedorafig        \
  --onefile               \
  --strip
