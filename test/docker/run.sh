#!/bin/bash

trap 'rm ../../Dockerfile; exit' INT

cp -f Dockerfile ../../
if ! docker buildx build -t test-img ../../; then
  echo "DockerTestError: Docker build failed" >&2
  kill -INT $$
fi

if ! docker run --rm -it test-img; then
  # echo "Tests failed." >&2
  # TODO: Add tests to run in docker automatically on start.
  kill -INT $$
fi
rm ../../Dockerfile
