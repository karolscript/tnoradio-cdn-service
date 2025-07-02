# Quick Setup Guide for CDN Service

## Your Repository Details
- **GitHub Repository**: https://github.com/karolscript/tnoradio-cdn-service.git
- **VPS IP**: 82.25.79.43
- **Service Port**: 19000

## Step 1: Jenkins Job Creation

### 1.1 Create New Job
1. Go to your Jenkins dashboard
2. Click "New Item"
3. Enter job name: `cdn-service-deploy`
4. Select "Pipeline"
5. Click "OK"

### 1.2 Configure Job Settings

**General Tab:**
- ✅ **Discard old builds**
  - Days to keep builds: `30`
  - Max # of builds to keep: `50`

**Build Triggers Tab:**
- ✅ **Generic Webhook Trigger**
  - Token: `jenkins-webhook-lechuzas-cdn`

**Pipeline Tab:**
- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/karolscript/tnoradio-cdn-service.git`
- **Branch Specifier**: `*/main`
- **Script Path**: `Jenkinsfile`

### 1.3 Save the Job
Click "Save" to create the job.

## Step 2: SSH Credentials Setup

### 2.1 Add SSH Credentials
1. Go to: **Manage Jenkins** → **Manage Credentials**
2. Click: **System** → **Global credentials** → **Add Credentials**
3. Configure:
   - **Kind**: SSH Username with private key
   - **Scope**: Global
   - **ID**: `vps-ssh-key`
   - **Description**: VPS SSH Key for CDN Service
   - **Username**: `root`
   - **Private Key**: Enter your VPS private key
   - **Passphrase**: (if your key has one)

## Step 3: GitHub Webhook Setup

### 3.1 Configure Webhook
1. Go to: https://github.com/karolscript/tnoradio-cdn-service
2. Click: **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `http://YOUR-JENKINS-SERVER:8080/generic-webhook-trigger/invoke`
   - **Content type**: `application/json`
   - **Secret**: (leave empty)
   - **Events**: Just the push event
   - **Active**: ✅ Checked

### 3.2 Test Webhook
After adding the webhook, make a test commit:
```bash
git add .
git commit -m "Test webhook trigger"
git push origin main
```

## Step 4: Test the Pipeline

### 4.1 Manual Test
1. Go to your Jenkins job
2. Click "Build Now"
3. Monitor the build console output

### 4.2 Verify Deployment
After successful build, test the endpoints:
```bash
# Test health endpoint
curl http://82.25.79.43/health

# Test videos endpoint
curl "http://82.25.79.43/get_videos?collection=trailers"

# Test CORS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://82.25.79.43/get_videos
```

## Step 5: VPS Management

### 5.1 Use VPS Manager Script
```bash
# Check service status
./vps-manager.sh status

# View logs
./vps-manager.sh logs

# Test endpoints
./vps-manager.sh test-endpoints

# Restart service if needed
./vps-manager.sh restart
```

### 5.2 Connect to VPS
```bash
# SSH to VPS
./vps-manager.sh connect

# Or direct SSH
ssh root@82.25.79.43
```

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   ```bash
   # Test SSH manually
   ssh root@82.25.79.43
   
   # Check Jenkins credentials
   # Verify SSH key is correct
   ```

2. **Webhook Not Triggering**
   ```bash
   # Test webhook manually
   curl -X POST http://YOUR-JENKINS-SERVER:8080/generic-webhook-trigger/invoke \
        -H "Content-Type: application/json" \
        -d '{"repository":{"name":"tnoradio-cdn-service"},"ref":"refs/heads/main"}'
   ```

3. **Service Not Responding**
   ```bash
   # Check service status
   ./vps-manager.sh status
   
   # View logs
   ./vps-manager.sh logs
   
   # Restart service
   ./vps-manager.sh restart
   ```

### Environment Variables
Make sure your VPS has the required environment variables in `/opt/tnoradio-cdn-service/.env`:
```bash
BUNNY_STORAGE_API_KEY=your_actual_api_key
BUNNY_API_KEY=your_actual_api_key
BUNNY_VIDEO_LIBRARY_ID=286671
```

## Next Steps

1. **Replace `YOUR-JENKINS-SERVER`** with your actual Jenkins server URL
2. **Set up SSH credentials** with your VPS private key
3. **Configure the webhook** with the correct Jenkins URL
4. **Test the complete pipeline**
5. **Monitor the service** using the VPS manager script

## Support Files

- `Jenkinsfile` - Pipeline definition
- `vps-manager.sh` - VPS management script
- `test_cdn.py` - Service testing script
- `DEPLOYMENT_GUIDE.md` - Detailed deployment guide
- `JENKINS_SETUP_GUIDE.md` - Complete Jenkins setup guide 