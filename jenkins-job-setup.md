# Jenkins Job Setup Guide

## Problem Fixed
The Jenkins job was failing because it was trying to fetch from the `master` branch, but your repository uses `main` as the default branch.

## Changes Made
1. **Updated Jenkinsfile** to explicitly specify the `main` branch
2. **Updated webhook trigger** to work with GitHub instead of Bitbucket
3. **Added branch filtering** to only trigger on `main` branch pushes

## Jenkins Job Configuration

### 1. Repository Configuration
In your Jenkins job configuration, make sure:

**Source Code Management → Git**
- **Repository URL**: `https://github.com/karolscript/tnoradio-cdn-service.git`
- **Branches to build**: `*/main`
- **Credentials**: (if needed, add your GitHub credentials)

### 2. Build Triggers
**Build Triggers → Generic Webhook Trigger**
- **Token**: `jenkins-webhook-lechuzas-cdn`
- **Generic Variables**:
  - `ref` → `$.ref`
  - `repository` → `$.repository.name`
  - `branch` → `$.ref_name`
- **Expression filter**: `$ref`
- **Text**: `refs/heads/main`

### 3. Pipeline Configuration
**Pipeline → Definition**: `Pipeline script from SCM`
- **SCM**: Git
- **Repository URL**: `https://github.com/karolscript/tnoradio-cdn-service.git`
- **Branches to build**: `*/main`
- **Script Path**: `Jenkinsfile`

## GitHub Webhook Configuration

### Webhook URL
Use your localtunnel URL:
```
https://tnoradio-cdn.loca.lt/generic-webhook-trigger/invoke
```

### Webhook Settings
- **Content type**: `application/json`
- **Secret**: (leave empty)
- **Events**: Just the push event
- **Active**: ✅ Checked

## Testing the Setup

1. **Make a test commit**:
   ```bash
   git add .
   git commit -m "Test Jenkins job with main branch"
   git push origin main
   ```

2. **Check Jenkins**:
   - Go to your Jenkins dashboard
   - Look for the `cdn-service-deploy` job
   - Check if it was triggered successfully

3. **Check webhook delivery**:
   - Go to GitHub repository settings
   - Check webhook delivery logs

## Troubleshooting

### If Jenkins still fails:

1. **Check branch configuration**:
   - Verify Jenkins job is configured for `main` branch
   - Check that the repository URL is correct

2. **Check webhook delivery**:
   - Look at GitHub webhook delivery logs
   - Verify the webhook URL is accessible

3. **Check Jenkins logs**:
   - Look at the build console output
   - Check for any authentication issues

### Common Issues:

1. **Authentication**: If using private repository, add GitHub credentials to Jenkins
2. **Webhook URL**: Make sure localtunnel is running and URL is correct
3. **Branch name**: Ensure both Jenkins and webhook are configured for `main`

## Manual Job Trigger

If you need to trigger the job manually:
1. Go to Jenkins dashboard
2. Find your job (`cdn-service-deploy`)
3. Click "Build Now"

## Next Steps

Once the job is working:
1. Test the full deployment pipeline
2. Verify the CDN service is deployed to your VPS
3. Test the service endpoints
4. Set up monitoring and logging 