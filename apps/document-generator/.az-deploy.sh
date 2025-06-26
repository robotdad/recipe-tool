#!/bin/bash
# Simple Azure deployment script

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./.az-deploy.sh <APP_NAME> <RESOURCE_GROUP>"
    exit 1
fi

echo "Deploying to Azure..."
echo "App Name: $1"
echo "Resource Group: $2"

# Use az webapp up for simplicity - it handles everything
az webapp up \
  --name "$1" \
  --resource-group "$2" \
  --runtime "PYTHON:3.11" \
  --sku B1 \
  --logs