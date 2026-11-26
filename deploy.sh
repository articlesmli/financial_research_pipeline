#!/bin/bash
set -e

SERVER_IP="10.97.0.251"
SSH_USER="ubuntu"
SSH_KEY="$HOME/.ssh/mock_server_key"

echo "Connecting to mock server at $SERVER_IP..."

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" << 'REMOTE_COMMANDS'
  echo "Logged into mock server successfully!"
  # Create app directory if it doesn't exist
  mkdir -p ~/my-app
  cd ~/my-app
  
  echo "Mock server deployment directory ready at ~/my-app"
REMOTE_COMMANDS

echo "Deployment test completed successfully!"
