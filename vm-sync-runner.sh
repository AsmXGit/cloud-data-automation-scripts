#!/bin/bash

# Set strict mode
set -euo pipefail

# Define usage message
USAGE="Usage: $0 <SOURCE> <TARGET>"

# Check if required arguments are provided
if [ $# -ne 2 ]; then
  echo "$USAGE"
  exit 1
fi

# Define variables
SOURCE="$1"
TARGET="$2"
INTERIM=$(basename "$SOURCE")
CLUSTER_FILE="cluster"
PRIVATE_KEY="./security.pem"
LOG_FILE="deployment.log"

# Validate cluster file existence
if [ ! -f "$CLUSTER_FILE" ]; then
  echo "Error: Cluster file '$CLUSTER_FILE' not found."
  exit 1
fi

# Validate private key existence
if [ ! -f "$PRIVATE_KEY" ]; then
  echo "Error: Private key '$PRIVATE_KEY' not found."
  exit 1
fi

# Create log file
touch "$LOG_FILE"

# Iterate over cluster nodes
for NODE in $(cat "$CLUSTER_FILE"); do
  # Copy file to node
  scp -i "$PRIVATE_KEY" -o StrictHostKeyChecking=no "$SOURCE" "centos@$NODE:~/"
  STATUS=$?
  
  # Log result
  if [ $STATUS -eq 0 ]; then
    echo "[$(date)] Successfully copied file to $NODE." >> "$LOG_FILE"
  else
    echo "[$(date)] Failed to copy file to $NODE. Exit code: $STATUS" >> "$LOG_FILE"
    continue
  fi
  
  # Copy file to target location on node
  ssh -t -i "$PRIVATE_KEY" -o StrictHostKeyChecking=no "centos@$NODE" "sudo cp $INTERIM $TARGET"
  STATUS=$?
  
  # Log result
  if [ $STATUS -eq 0 ]; then
    echo "[$(date)] Successfully deployed file on $NODE." >> "$LOG_FILE"
  else
    echo "[$(date)] Failed to deploy file on $NODE. Exit code: $STATUS" >> "$LOG_FILE"
  fi
done
