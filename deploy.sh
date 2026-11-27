#!/bin/bash
set -e

SERVER_IP="10.97.0.251"
SSH_USER="ubuntu"
SSH_KEY="$HOME/.ssh/mock_server_key"

echo "Connecting to mock server at $SERVER_IP..."

# 1. Ensure remote app directory exists
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" "mkdir -p ~/my-app/src ~/my-app/wheelhouse"

# 2. Transfer project files, wheelhouse, and offline base image
echo "Transferring project files, wheelhouse, and offline base image..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no docker-compose.yaml "$SSH_USER@$SERVER_IP:~/my-app/"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no Dockerfile.* "$SSH_USER@$SERVER_IP:~/my-app/"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no requirements.txt "$SSH_USER@$SERVER_IP:~/my-app/"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no python-slim.tar "$SSH_USER@$SERVER_IP:~/my-app/"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no -r src/* "$SSH_USER@$SERVER_IP:~/my-app/src/"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no -r wheelhouse/* "$SSH_USER@$SERVER_IP:~/my-app/wheelhouse/"

# 3. Load base image, build, and start containers locally on the mock server
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" << 'REMOTE_COMMANDS'
  cd ~/my-app
  echo "Loading offline base image..."
  docker load -i python-slim.tar
  echo "Building and starting containers on mock server..."
  docker compose up -d --build
  echo "Containers started successfully!"
REMOTE_COMMANDS

echo "Full local deployment pipeline completed successfully!"