#!/bin/bash
# Azure deployment script for document-generator

# Check for required parameters
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./deploy.sh <APP_NAME> <RESOURCE_GROUP>"
    echo "Example: ./deploy.sh my-app-name my-resource-group"
    exit 1
fi

APP_NAME=$1
RESOURCE_GROUP=$2

echo "Creating deployment package..."
python3 -c "
import zipfile
import os

exclude_dirs = {'__pycache__', 'tests', '.vscode', '.git'}
exclude_files = {'.pyc', 'pytest.log', 'deploy.zip', '.tar.gz'}
exclude_patterns = ['.deployment', '.ruff.toml', '.deploymentignore']

with zipfile.ZipFile('deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            filepath = os.path.join(root, file)
            if any(file.endswith(ext) for ext in exclude_files):
                continue
            if any(pattern in file for pattern in exclude_patterns):
                continue
            if file.startswith('.'):
                continue
            arcname = filepath[2:] if filepath.startswith('./') else filepath
            zf.write(filepath, arcname)
"

echo "Deploying to Azure App Service..."
az webapp deploy \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --src-path deploy.zip \
  --type zip

echo "Cleaning up..."
rm deploy.zip

echo "Deployment complete! Check logs with:"
echo "az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"