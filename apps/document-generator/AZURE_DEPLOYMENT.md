# Azure App Service Deployment - Quick Guide

Simple deployment guide for hosting the Document Generator on Azure App Service with managed identity.

## Prerequisites

- Azure subscription
- Azure OpenAI resource
- User-assigned managed identity (already created)

## Deployment Steps

### 1. Create App Service

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"** → **"Web App"**
3. Fill in:
   - **Name**: `document-generator-app` (or your choice)
   - **Runtime**: `Python 3.11`
   - **Operating System**: `Linux`
   - **Region**: Same as your Azure OpenAI resource
4. Click **"Review + create"** → **"Create"**

### 2. Secure with Azure AD Authentication (Recommended)

Secure your app before deployment to prevent unauthorized access:

#### A. Configure Authentication on Web App

1. In your web app resource, navigate to **"Settings"** → **"Authentication"**
2. Click **"Add identity provider"**
3. Set the following:
   - **Identity provider**: Microsoft
   - **Application (client) ID**: `<YOUR-APP-REGISTRATION-CLIENT-ID>`
   - **Allowed tenants**: `<YOUR-TENANT-ID>` (for single tenant access)
4. Click **"Add"**
5. Navigate to **"Overview"** → Note the **"Default domain"** (needed for next step)

#### B. Configure App Registration

1. Go to your app registration in Azure AD
2. Navigate to **"Manage"** → **"Authentication"**
3. Find **"Platform configurations"** → **"Single-page application"** → **"Redirect URIs"**
4. Click **"Add URI"**
5. Add a new entry using your default domain:
   ```
   https://<YOUR-DEFAULT-DOMAIN>/.auth/login/aad/callback
   ```
6. Click **"Save"**

**Note**: If you delete the web app later, remember to remove its redirect URI from the app registration to keep it clean.

### 3. Assign Managed Identity

1. Go to your new App Service
2. Left menu → **"Identity"**
3. **"User assigned"** tab → **"Add"**
4. Select your existing managed identity
5. Click **"Add"**

### 4. Configure App Service

#### A. Set Startup Command

1. Left menu → **"Configuration"**
2. **"General settings"** tab
3. **Startup Command**: `python startup.py`
4. Click **"Save"**

#### B. Configure Environment Variables

1. **"Application settings"** tab
2. Click **"Advanced edit"**
3. Add these entries to the existing JSON array (don't replace the entire array):

```json
[
  {
    "name": "GRADIO_SERVER_NAME",
    "value": "0.0.0.0",
    "slotSetting": false
  },
  {
    "name": "GRADIO_SERVER_PORT",
    "value": "8000",
    "slotSetting": false
  },
  {
    "name": "SCM_DO_BUILD_DURING_DEPLOYMENT",
    "value": "true",
    "slotSetting": false
  },
  {
    "name": "AZURE_OPENAI_BASE_URL",
    "value": "https://<YOUR-OPENAI-RESOURCE>.azurewebsites.net",
    "slotSetting": false
  },
  {
    "name": "AZURE_USE_MANAGED_IDENTITY",
    "value": "true",
    "slotSetting": false
  },
  {
    "name": "AZURE_CLIENT_ID",
    "value": "<YOUR-MANAGED-IDENTITY-CLIENT-ID>",
    "slotSetting": false
  }
]
```

4. **Replace the placeholder values:**
   - `<YOUR-OPENAI-RESOURCE>` → Your Azure OpenAI resource name
   - `<YOUR-MANAGED-IDENTITY-CLIENT-ID>` → Your managed identity's client ID
5. Click **"OK"** → **"Save"** → **"Continue"**

### 5. Quick Verification

Before deploying code, verify your App Service is properly configured:

1. Go to **"Overview"** → Click your app URL
2. You should see Azure AD login (if configured) or a default App Service page
3. Check basic health:
   ```bash
   curl https://<YOUR-APP-NAME>.azurewebsites.net
   ```
   Should return HTML content (login page or default page)

### 6. Deploy Application

**Important for Monorepo**: If deploying from a monorepo, ensure `.deployment` file exists in repository root with:
```
[config]
project = apps/document-generator
```

#### Option A: VS Code Azure Extension 

**⚠️ Note**: VS Code deployment from monorepos can be problematic. Use Option B (Azure CLI) if you encounter issues.

1. **Install Extension:**
   - **"Azure App Service"** (ms-azuretools.vscode-azureappservice)

2. **Sign In:**
   - Press `Ctrl+Shift+P` → Type "Azure: Sign In"
   - Follow authentication prompts

3. **Deploy:**
   - **Important**: Open VS Code at the repository root (not in subfolder)
   - Press `Ctrl+Shift+P` → Type "Azure App Service: Deploy to Web App"
   - Select your subscription → Select your App Service
   - When prompted for folder, browse to `apps/document-generator`
   - Confirm deployment

4. **Monitor:**
   - View deployment progress in VS Code output panel
   - Check Azure extension sidebar for deployment status

#### Option B: Azure CLI (Recommended for Monorepos)

1. **Install Azure CLI** (if not already installed)
2. **Sign In:**
   ```bash
   az login
   ```
3. **Deploy directly from folder:**
   ```bash
   cd apps/document-generator
   az webapp up \
     --name <YOUR-APP-NAME> \
     --resource-group <YOUR-RESOURCE-GROUP> \
     --runtime "PYTHON:3.11" \
     --sku B1
   ```
   
   Or if app already exists:
   ```bash
   cd apps/document-generator
   az webapp deploy \
     --name <YOUR-APP-NAME> \
     --resource-group <YOUR-RESOURCE-GROUP> \
     --type zip \
     --src-path .
   ```

4. **Monitor deployment:**
   ```bash
   az webapp log tail --name <YOUR-APP-NAME> --resource-group <YOUR-RESOURCE-GROUP>
   ```

### 7. Verify Deployment

1. Go to **"Overview"** → Click your app URL
2. Document generator should load
3. Test document generation with Azure OpenAI

## Troubleshooting

**Build fails with "No matching distribution found"?**
- Check requirements.txt for local packages not available on PyPI
- Remove any internal/monorepo package references
- Ensure all packages are publicly available

**Files not appearing in /home/site/wwwroot?**
- This is normal for Python apps with build automation
- Check logs for build failures preventing deployment
- Verify requirements.txt installs successfully
- For monorepo: ensure `.deployment` file exists with `project = apps/document-generator`

**App won't start?**
- Check **"Log stream"** in Azure Portal for specific error messages
- Verify startup command is set to `python startup.py`

**Azure OpenAI connection fails?**
- Verify managed identity has "Cognitive Services OpenAI User" role on your Azure OpenAI resource
- Confirm `AZURE_CLIENT_ID` matches your managed identity's client ID

## Required Files

Essential files for deployment (in order of importance):

1. `startup.py` - App Service entry point
2. `requirements.txt` - Python dependencies
3. `runtime.txt` - Should contain: `python-3.11`
4. `document_generator_app/` - Application code directory

That's it! Your document generator is now live with secure Azure OpenAI access.
