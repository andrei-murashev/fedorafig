#!/bin/bash

handle_error() {
  MSG="ERROR: $1"
  echo "$MSG" >&2
  echo "$MSG" >> log.txt
  exit 1
}


DOCKERFILE='fedora40-setup.dockerfile'
IMAGE_NAME="${DOCKERFILE%%.*}"
CONTAINER_NAME="$IMAGE_NAME-container"

if [ ! "$(docker ps -a | grep $CONTAINER_NAME)" ] || [ "$1" == 'RESET' ]; then
    rm -rf log.txt || true
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

    if ! docker buildx build -f "$DOCKERFILE" -t "$IMAGE_NAME" ../../; then
      handle_error "Docker could not build from $DOCKERFILE"
    fi; if ! docker run --name "$CONTAINER_NAME" -t "$IMAGE_NAME"; then
      handle_error "Docker failed to finishing running from $DOCKERFILE"
    fi; if ! docker commit "$CONTAINER_NAME" "${IMAGE_NAME}"; then
      handle_error "Failed to commit Docker container $CONTAINER_NAME"
    fi
fi


DOCKERFILE='fedora40-test.dockerfile'
IMAGE_NAME="${DOCKERFILE%%.*}"
CONTAINER_NAME="$IMAGE_NAME-container"

if ! docker buildx build -f "$DOCKERFILE" -t "$IMAGE_NAME" ../../; then
  handle_error "Docker could not build from $DOCKERFILE"
fi; if ! docker run --name "$CONTAINER_NAME" --rm -it "$IMAGE_NAME"; then
  handle_error "Docker failed to finish running from $DOCKERFILE"
fi
