#!/bin/bash

handle_error() {
  MSG="ERROR $1"
  echo "$MSG" >&2
  echo "$MSG" >> log.txt
  exit 1
}


DOCKERFILE='fedora40-try.dockerfile'
IMAGE_NAME="${DOCKERFILE%%.*}"

if ! docker buildx build -f "$DOCKERFILE" -t "$IMAGE_NAME" ../../; then
  handle_error "Docker could not build from $DOCKERFILE"
fi; if ! docker run --rm -it "$IMAGE_NAME"; then
  handle_error "Docker failed to run from $DOCKERFILE"
fi
