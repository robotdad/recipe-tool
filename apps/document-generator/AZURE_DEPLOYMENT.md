# Azure App Service Deployment - Quick Guide

Simple deployment guide for hosting the Document Generator on Azure App Service with managed identity.

## 📋 Prerequisites

- Azure subscription
- Azure OpenAI resource
- User-assigned managed identity (already created)

## 🚀 Deployment Steps

### 1. Create App Service

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"** → **"Web App"**
3. Fill in:
   - **Name**: `document-generator-app` (or your choice)
   - **Runtime**: `Python 3.11`
   - **Operating System**: `Linux`
   - **Region**: Same as your Azure OpenAI resource
4. Click **"Review + create"** → **"Create"**

### 2. Assign Managed Identity

1. Go to your new App Service
2. Left menu → **"Identity"**
3. **"User assigned"** tab → **"Add"**
4. Select your existing managed identity
5. Click **"Add"**

### 3. Configure App Service

#### A. Set Startup Command
1. Left menu → **"Configuration"**
2. **"General settings"** tab
3. **Startup Command**: `python startup.py`
4. Click **"Save"**

#### B. Configure Environment Variables
1. **"Application settings"** tab
2. Click **"+ New application setting"** for each:

```
GRADIO_SERVER_NAME = 0.0.0.0
GRADIO_SERVER_PORT = 8000
SCM_DO_BUILD_DURING_DEPLOYMENT = true
AZURE_OPENAI_BASE_URL = https://your-openai-resource.openai.azure.com/
AZURE_USE_MANAGED_IDENTITY = true
AZURE_CLIENT_ID = your-managed-identity-client-id
```

3. Click **"Save"** → **"Continue"**

### 4. Deploy Application

#### Option A: VS Code Azure Extension (Best for Enterprise)
1. **Install Extensions:**
   - **"Azure App Service"** (ms-azuretools.vscode-azureappservice)
   - **"Azure Account"** (ms-vscode.azure-account)

2. **Sign In:**
   - Press `Ctrl+Shift+P` → Type "Azure: Sign In"
   - Follow authentication prompts

3. **Deploy:**
   - Open `apps/document-generator/` folder in VS Code
   - Press `Ctrl+Shift+P` → Type "Azure App Service: Deploy to Web App"
   - OR right-click folder → **"Deploy to Web App..."**
   - Select your subscription → Select your App Service
   - Confirm deployment

4. **Monitor:**
   - View deployment progress in VS Code output panel
   - Check Azure extension sidebar for deployment status

#### Option B: Azure CLI
1. **Install Azure CLI** (if not already installed)
2. **Sign In:**
   ```bash
   az login
   ```
3. **Create ZIP file:**
   ```bash
   cd apps/document-generator
   zip -r ../document-generator.zip . -x ".*" "__pycache__/*" "*.pyc"
   ```
4. **Deploy:**
   ```bash
   az webapp deployment source config-zip \
     --name document-generator-app \
     --resource-group your-resource-group \
     --src ../document-generator.zip
   ```
5. **Monitor deployment:**
   ```bash
   az webapp log tail --name document-generator-app --resource-group your-resource-group
   ```

### 5. Verify Deployment

1. Go to **"Overview"** → Click your app URL
2. Document generator should load
3. Test document generation with Azure OpenAI

## 🛠️ Quick Fixes

**App won't start?**
- Check **"Log stream"** for errors
- Verify all environment variables are set

**Azure OpenAI not working?**
- Verify managed identity has "Cognitive Services OpenAI User" role
- Check Azure OpenAI URL format: `https://name.openai.azure.com/`

**Import errors?**
- Deploy with all required files from `apps/document-generator/`
- Include the deployment files (startup.py, requirements.txt, etc.)

## 📝 Files Needed

Make sure your deployment includes:
- `document_generator_app/` (all Python code)
- `startup.py`
- `requirements.txt`
- `runtime.txt`

**Note**: Remove `.deployment`, `deploy.cmd`, `deploy.sh`, and `web.config` files - they're not needed for Linux App Service.

That's it! Your document generator is now live with secure Azure OpenAI access. 🎉