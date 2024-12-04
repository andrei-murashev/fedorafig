#!/bin/bash

if ! docker buildx build -t fedora40-test .; then
  echo "DockerTestError: Docker build failed" >&2
fi

if ! docker run --rm -it fedora40-test; then
  # echo "Tests failed." >&2
  exit 1
fi
