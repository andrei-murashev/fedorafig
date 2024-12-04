#!/bin/bash

if ! docker buildx build --build-arg CACHE_BUST=$(date +%s) -t fedora40-test .; then
  echo "DockerTestError: Docker build failed" >&2
  exit 1
fi

if ! docker run --rm -it fedora40-test; then
  # echo "Tests failed." >&2
  exit 1
fi
