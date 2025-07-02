# GitHub Webhook Setup with ngrok for Local Jenkins

## Problem
GitHub webhooks can't reach `localhost` because it's not accessible over the public internet. We need to expose your local Jenkins to the internet.

## Solution: Use ngrok

ngrok creates a secure tunnel to your local Jenkins server, making it accessible to GitHub webhooks.

## Step-by-Step Setup

### 1. Start Jenkins (if not already running)
Make sure Jenkins is running on your local machine:
```bash
# Check if Jenkins is running
curl http://localhost:8080
```

### 2. Start ngrok Tunnel
Run the ngrok setup script:
```bash
./setup-ngrok.sh
```

This will:
- Check if Jenkins is running
- Start ngrok tunnel
- Display your public URL
- Save URLs to files for easy access

### 3. Get Your Public URL
The script will show you something like:
```
Your Jenkins Public URL:
https://abc123.ngrok.io

GitHub Webhook Payload URL:
https://abc123.ngrok.io/generic-webhook-trigger/invoke
```

### 4. Configure GitHub Webhook

1. **Go to your GitHub repository**:
   https://github.com/karolscript/tnoradio-cdn-service

2. **Navigate to Settings**:
   - Click "Settings" tab
   - Click "Webhooks" in the left sidebar
   - Click "Add webhook"

3. **Configure the webhook**:
   - **Payload URL**: `https://abc123.ngrok.io/generic-webhook-trigger/invoke`
     (Use the URL from step 3)
   - **Content type**: `application/json`
   - **Secret**: (leave empty)
   - **Which events would you like to trigger this webhook?**: 
     - Select "Just the push event"
   - **Active**: ✅ Checked

4. **Click "Add webhook"**

### 5. Test the Webhook

1. **Make a test commit**:
   ```bash
   git add .
   git commit -m "Test webhook with ngrok"
   git push origin main
   ```

2. **Check Jenkins**:
   - Go to your Jenkins dashboard
   - Look for the `cdn-service-deploy` job
   - Check if it was triggered

3. **Check webhook delivery**:
   - Go back to GitHub webhook settings
   - Click on your webhook
   - Scroll down to "Recent Deliveries"
   - Check if the delivery was successful (green checkmark)

## Alternative Solutions

### Option 1: Use a Cloud Jenkins Server
Instead of local Jenkins, use:
- Jenkins on AWS/GCP/Azure
- Jenkins on your VPS (82.25.79.43)
- Jenkins as a Service (Jenkins Cloud)

### Option 2: Use GitHub Actions
Replace Jenkins with GitHub Actions for CI/CD:
```yaml
# .github/workflows/deploy.yml
name: Deploy CDN Service
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to VPS
        run: |
          # Your deployment script
```

### Option 3: Use a Different Tunnel Service
Instead of ngrok, you can use:
- **Cloudflare Tunnel**: `cloudflared tunnel --url localhost:8080`
- **LocalTunnel**: `npx localtunnel --port 8080`
- **Serveo**: `ssh -R 80:localhost:8080 serveo.net`

## Troubleshooting

### ngrok Issues

1. **ngrok not starting**:
   ```bash
   # Check if port 8080 is available
   lsof -i :8080
   
   # Start Jenkins if not running
   # Then try ngrok again
   ```

2. **Authentication required**:
   ```bash
   # Sign up at https://ngrok.com
   # Get your authtoken
   ngrok config add-authtoken YOUR_TOKEN
   ```

3. **URL not working**:
   ```bash
   # Check ngrok status
   curl http://localhost:4040/api/tunnels
   
   # Restart ngrok
   pkill ngrok
   ./setup-ngrok.sh
   ```

### Webhook Issues

1. **Webhook not delivering**:
   - Check if ngrok tunnel is still running
   - Verify the webhook URL is correct
   - Check GitHub webhook logs

2. **Jenkins not receiving webhook**:
   - Verify Jenkins is running
   - Check Jenkins logs
   - Test webhook manually:
   ```bash
   curl -X POST https://your-ngrok-url/generic-webhook-trigger/invoke \
        -H "Content-Type: application/json" \
        -d '{"repository":{"name":"tnoradio-cdn-service"},"ref":"refs/heads/main"}'
   ```

## Security Considerations

1. **ngrok URLs are public**: Anyone with the URL can access your Jenkins
2. **Use authentication**: Set up Jenkins authentication
3. **Limit access**: Use ngrok authentication for more control
4. **Monitor logs**: Check for unauthorized access

## Production Setup

For production, consider:
1. **Move Jenkins to your VPS**: Use your existing VPS (82.25.79.43)
2. **Use a domain**: Set up a proper domain for Jenkins
3. **SSL certificates**: Use HTTPS for security
4. **Firewall rules**: Restrict access to necessary IPs

## Quick Commands

```bash
# Start ngrok tunnel
./setup-ngrok.sh

# Check ngrok status
curl http://localhost:4040/api/tunnels

# Test webhook manually
curl -X POST https://your-ngrok-url/generic-webhook-trigger/invoke \
     -H "Content-Type: application/json" \
     -d '{"repository":{"name":"tnoradio-cdn-service"},"ref":"refs/heads/main"}'

# Stop ngrok
pkill ngrok
``` 