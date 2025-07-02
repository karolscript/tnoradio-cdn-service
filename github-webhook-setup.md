# GitHub Webhook Setup for Jenkins

## Step 1: Configure GitHub Repository Webhook

1. **Go to your GitHub repository**
   - Navigate to: `https://github.com/your-username/TNONetwork`

2. **Access Repository Settings**
   - Click on "Settings" tab
   - Click on "Webhooks" in the left sidebar
   - Click "Add webhook"

3. **Configure Webhook**
   - **Payload URL**: `http://your-jenkins-server:8080/generic-webhook-trigger/invoke`
   - **Content type**: `application/json`
   - **Secret**: Leave empty (or create a secret if needed)
   - **Which events would you like to trigger this webhook?**: 
     - Select "Just the push event"
   - **Active**: ✅ Checked

4. **Advanced Settings**
   - **SSL verification**: ✅ Checked (if using HTTPS)
   - Click "Add webhook"

## Step 2: Verify Webhook Configuration

After adding the webhook, you should see:
- ✅ Green checkmark indicating successful delivery
- Webhook listed in the webhooks page

## Step 3: Test Webhook

1. **Make a test commit**:
   ```bash
   git add .
   git commit -m "Test webhook trigger"
   git push origin main
   ```

2. **Check Jenkins**:
   - Go to your Jenkins dashboard
   - Look for the CDN service job
   - Check if it was triggered by the push

## Troubleshooting

### If webhook doesn't work:

1. **Check Jenkins URL**:
   - Ensure Jenkins is accessible from GitHub
   - Verify the webhook URL is correct

2. **Check Jenkins Logs**:
   - Go to Jenkins > Manage Jenkins > System Log
   - Look for webhook-related errors

3. **Test webhook manually**:
   ```bash
   curl -X POST http://your-jenkins-server:8080/generic-webhook-trigger/invoke \
        -H "Content-Type: application/json" \
        -d '{"repository":{"name":"TNONetwork"},"ref":"refs/heads/main"}'
   ```

### Common Issues:

1. **Jenkins not accessible**: Make sure Jenkins is publicly accessible or use a tunnel
2. **Wrong URL**: Double-check the webhook URL
3. **SSL issues**: If using HTTPS, ensure certificates are valid
4. **Firewall**: Ensure port 8080 (or your Jenkins port) is open 