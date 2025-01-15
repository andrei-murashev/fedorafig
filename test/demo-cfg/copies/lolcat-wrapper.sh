#!/bin/bash

# Default configuration for lolcat
# Customize these options as needed

# Text to process
TEXT=$1

# Set default options
FREQUENCY=${FREQUENCY:-0.1}   # Set the frequency of color changes
SPEED=${SPEED:-20}            # Set the speed of scrolling text (for piped input)
FORCE=${FORCE:-false}         # Force color output even if not a terminal
SEED=${SEED:-12345}           # Set a seed for consistent colors
ANIMATE=${ANIMATE:-false}     # Animate text with rainbow colors

# Build lolcat command
COMMAND="lolcat"

# Add options
[ "$FORCE" = "true" ] && COMMAND+=" --force"
[ "$ANIMATE" = "true" ] && COMMAND+=" --animate --speed=$SPEED"
COMMAND+=" --freq=$FREQUENCY --seed=$SEED"

# Execute lolcat with options
if [ -n "$TEXT" ]; then
  echo "$TEXT" | $COMMAND
else
  $COMMAND
fi
