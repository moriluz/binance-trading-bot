#!/bin/bash
set -e

# Configuration
IMAGE_NAME="moriluz88/trading-bot"
TAG="latest"

# Build the Docker image
echo "Building Docker image: ${IMAGE_NAME}:${TAG}"
docker build -t ${IMAGE_NAME}:${TAG} .

# Push the Docker image to the registry
echo "Pushing Docker image to registry: ${IMAGE_NAME}:${TAG}"
docker push ${IMAGE_NAME}:${TAG}

echo "Done!"
