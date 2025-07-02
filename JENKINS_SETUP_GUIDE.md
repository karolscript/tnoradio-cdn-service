# Jenkins Job Setup Guide - Step by Step

This guide will walk you through creating a Jenkins job that automatically deploys the CDN service to your VPS when you push to GitHub.

## Prerequisites

- Jenkins server running and accessible
- GitHub repository with your code
- SSH access to your VPS (82.25.79.43)
- Jenkins plugins installed (see below)

## Step 1: Install Required Jenkins Plugins

1. **Go to Jenkins Dashboard**
   - Navigate to: `http://your-jenkins-server:8080`

2. **Manage Jenkins**
   - Click "Manage Jenkins" in the left sidebar
   - Click "Manage Plugins"

3. **Install Required Plugins**
   Go to the "Available" tab and install these plugins:
   - ✅ **Generic Webhook Trigger** (for GitHub webhooks)
   - ✅ **Pipeline** (for Jenkinsfile support)
   - ✅ **Git** (for GitHub integration)
   - ✅ **SSH Agent** (for VPS deployment)
   - ✅ **Credentials Binding** (for secure credentials)

4. **Restart Jenkins**
   - After installing plugins, restart Jenkins when prompted

## Step 2: Configure SSH Credentials for VPS

1. **Go to Credentials**
   - Click "Manage Jenkins" → "Manage Credentials"
   - Click "System" → "Global credentials" → "Add Credentials"

2. **Add SSH Credentials**
   - **Kind**: SSH Username with private key
   - **Scope**: Global
   - **ID**: `vps-ssh-key`
   - **Description**: VPS SSH Key for CDN Service
   - **Username**: `root`
   - **Private Key**: Enter your private key or select "From a file on Jenkins master"
   - **Passphrase**: (if your key has one)
   - Click "OK"

## Step 3: Create the Jenkins Job

### Option A: Create Job Manually

1. **Create New Job**
   - Click "New Item" on Jenkins dashboard
   - Enter job name: `cdn-service-deploy`
   - Select "Pipeline"
   - Click "OK"

2. **Configure Job**
   - **Description**: `CDN Service deployment pipeline for VPS (82.25.79.43)`
   - **Discard old builds**: Check "Discard old builds"
     - **Days to keep builds**: 30
     - **Max # of builds to keep**: 50

3. **Pipeline Configuration**
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: `https://github.com/your-username/TNONetwork.git`
   - **Credentials**: Add your GitHub credentials if private repo
   - **Branch Specifier**: `*/main` (or your main branch)
   - **Script Path**: `tnoradio-cdn-service/Jenkinsfile`

4. **Build Triggers**
   - Check "Generic Webhook Trigger"
   - **Token**: `jenkins-webhook-lechuzas-cdn`
   - **Generic Variables**:
     - **Key**: `ref`, **Value**: `$.ref`, **Expression Type**: JSONPath
     - **Key**: `repository`, **Value**: `$.repository.name`, **Expression Type**: JSONPath
     - **Key**: `branch`, **Value**: `$.ref`, **Expression Type**: JSONPath, **Regexp Filter**: `refs/heads/(.*)`

5. **Save the Job**

### Option B: Import Job Configuration

1. **Create Job from XML**
   - Click "New Item" → Enter name: `cdn-service-deploy` → Pipeline → OK
   - Go to "Configure"
   - Scroll to bottom and click "Pipeline Syntax"
   - Click "Load from file" and select the `jenkins-job-config.xml` file

## Step 4: Configure GitHub Webhook

1. **Get Jenkins Webhook URL**
   - Your webhook URL will be: `http://your-jenkins-server:8080/generic-webhook-trigger/invoke`

2. **Configure GitHub Webhook**
   - Go to your GitHub repository
   - Settings → Webhooks → Add webhook
   - **Payload URL**: `http://your-jenkins-server:8080/generic-webhook-trigger/invoke`
   - **Content type**: `application/json`
   - **Secret**: Leave empty
   - **Events**: Just the push event
   - Click "Add webhook"

3. **Test Webhook**
   - Make a test commit and push to trigger the job
   - Check Jenkins dashboard for the build

## Step 5: Configure Environment Variables

1. **Add Environment Variables**
   - Go to job configuration
   - In the pipeline script, you can add environment variables:
   ```groovy
   environment {
       VPS_IP = '82.25.79.43'
       VPS_USER = 'root'
       SERVICE_NAME = 'tnoradio-cdn-service'
       SERVICE_PORT = '19000'
   }
   ```

2. **Secure Credentials** (Optional)
   - For sensitive data, use Jenkins credentials:
   ```groovy
   environment {
       VPS_SSH_KEY = credentials('vps-ssh-key')
   }
   ```

## Step 6: Test the Pipeline

1. **Manual Build**
   - Click "Build Now" to test the pipeline manually
   - Monitor the build console output

2. **Check Build Logs**
   - Click on the build number
   - Click "Console Output" to see detailed logs

3. **Verify Deployment**
   - Check if the service is running on VPS
   - Test the endpoints:
   ```bash
   curl http://82.25.79.43/health
   curl "http://82.25.79.43/get_videos?collection=trailers"
   ```

## Step 7: Troubleshooting

### Common Issues and Solutions

1. **SSH Connection Failed**
   ```
   Solution: Verify SSH credentials and VPS accessibility
   - Test SSH manually: ssh root@82.25.79.43
   - Check Jenkins credentials configuration
   ```

2. **Permission Denied**
   ```
   Solution: Ensure proper permissions on VPS
   - Check if Jenkins can write to /opt/
   - Verify PM2 permissions
   ```

3. **Webhook Not Triggering**
   ```
   Solution: Check webhook configuration
   - Verify webhook URL is accessible
   - Check Jenkins logs for webhook errors
   - Test webhook manually with curl
   ```

4. **Nginx Configuration Error**
   ```
   Solution: Check nginx syntax
   - SSH to VPS and run: nginx -t
   - Check nginx error logs
   ```

### Debugging Commands

```bash
# Test SSH connection
ssh -o StrictHostKeyChecking=no root@82.25.79.43

# Check service status on VPS
pm2 status
systemctl status nginx

# Test endpoints
curl http://82.25.79.43/health
curl "http://82.25.79.43/get_videos?collection=trailers"

# Check logs
pm2 logs cdn
tail -f /var/log/nginx/error.log
```

## Step 8: Monitor and Maintain

1. **Set up Notifications**
   - Configure email notifications for build failures
   - Set up Slack/Discord notifications if needed

2. **Regular Maintenance**
   - Monitor disk space on VPS
   - Check PM2 logs regularly
   - Update dependencies periodically

3. **Backup Strategy**
   - Use the VPS manager script to create backups
   - Keep multiple versions of configurations

## Security Considerations

1. **SSH Keys**
   - Use dedicated SSH keys for Jenkins
   - Rotate keys regularly
   - Limit SSH access to necessary IPs

2. **Jenkins Security**
   - Enable authentication
   - Use HTTPS for Jenkins
   - Restrict access to Jenkins

3. **VPS Security**
   - Keep system updated
   - Configure firewall
   - Monitor logs for suspicious activity

## Next Steps

After setting up the Jenkins job:

1. **Test the complete pipeline** with a real code change
2. **Set up monitoring** for the deployed service
3. **Configure alerts** for service failures
4. **Document the process** for your team

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Jenkins and VPS logs
3. Test individual components manually
4. Use the VPS manager script for debugging

## Files Reference

- `Jenkinsfile` - Pipeline definition
- `jenkins-job-config.xml` - Job configuration for import
- `vps-manager.sh` - VPS management script
- `test_cdn.py` - Service testing script
- `nginx.conf` - Nginx configuration
- `ecosystem.config.js` - PM2 configuration 