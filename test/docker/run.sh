#!/bin/bash

cp -f Dockerfile ../../

# if ! docker buildx build --build-arg CACHE_BUST=$(date +%s) -t fedora40-test .; then
if ! docker buildx build -t test-img ../../; then
  echo "DockerTestError: Docker build failed" >&2
  # exit 1
fi

if ! docker run --rm -it test-img; then
  # echo "Tests failed." >&2
  exit 1
fi

rm ../../Dockerfile
