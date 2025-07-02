# CDN Service Deployment Guide

This guide explains how to deploy and manage the CDN service on your VPS (82.25.79.43).

## Prerequisites

- VPS with IP: 82.25.79.43
- SSH access to the VPS
- Python 3.8+ installed on VPS
- PM2 installed on VPS
- Nginx installed on VPS
- BunnyCDN API keys

## Quick Start

### 1. Deploy via Jenkins Pipeline

The easiest way to deploy is through the Jenkins pipeline:

1. Push your changes to the repository
2. The Jenkins pipeline will automatically:
   - Build the service
   - Deploy to VPS
   - Update nginx configuration
   - Test the endpoints

### 2. Manual Deployment

If you need to deploy manually:

```bash
# From your local machine
cd tnoradio-cdn-service

# Create deployment package
tar -czf cdn-service-deploy.tar.gz .

# Copy to VPS
scp cdn-service-deploy.tar.gz root@82.25.79.43:/tmp/
scp nginx.conf root@82.25.79.43:/tmp/
scp ecosystem.config.js root@82.25.79.43:/tmp/

# SSH to VPS and deploy
ssh root@82.25.79.43
```

## VPS Management Script

Use the `vps-manager.sh` script to manage the service:

```bash
# Make script executable (if not already)
chmod +x vps-manager.sh

# Check service status
./vps-manager.sh status

# View logs
./vps-manager.sh logs

# Restart service
./vps-manager.sh restart

# Test endpoints
./vps-manager.sh test-endpoints

# Connect to VPS
./vps-manager.sh connect

# Monitor service in real-time
./vps-manager.sh monitor
```

## Available Commands

| Command | Description |
|---------|-------------|
| `connect` | Connect to VPS via SSH |
| `status` | Check service status |
| `logs` | View service logs |
| `restart` | Restart CDN service |
| `stop` | Stop CDN service |
| `start` | Start CDN service |
| `nginx-status` | Check nginx status |
| `nginx-reload` | Reload nginx configuration |
| `nginx-test` | Test nginx configuration |
| `nginx-logs` | View nginx logs |
| `test-endpoints` | Test CDN endpoints |
| `update-env` | Update environment variables |
| `backup-config` | Backup current configuration |
| `restore-config` | Restore configuration from backup |
| `monitor` | Monitor service in real-time |

## Service Configuration

### Environment Variables

The service requires these environment variables in `/opt/tnoradio-cdn-service/.env`:

```bash
BUNNY_STORAGE_API_KEY=your_bunny_storage_api_key_here
BUNNY_API_KEY=your_bunny_api_key_here
BUNNY_VIDEO_LIBRARY_ID=286671
```

### Service Directory

The service is installed at: `/opt/tnoradio-cdn-service/`

### PM2 Configuration

The service runs under PM2 with the name `cdn`:

```bash
# Check PM2 status
pm2 status

# View PM2 logs
pm2 logs cdn

# Restart service
pm2 restart cdn
```

## Nginx Configuration

The service is proxied through nginx on port 80. The configuration includes:

- CORS headers for cross-origin requests
- Proxy to the CDN service on port 19000
- Health check endpoint at `/health`
- Videos endpoint at `/get_videos`

### Nginx Management

```bash
# Test nginx configuration
nginx -t

# Reload nginx
systemctl reload nginx

# View nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/get_videos` | GET | Get videos by collection |
| `/get_stream` | GET | Get video library list |
| `/get_stream_collections` | GET | Get collections list |
| `/get_video_by_title` | GET | Get video by title |

### Example Usage

```bash
# Health check
curl http://82.25.79.43/health

# Get trailers
curl "http://82.25.79.43/get_videos?collection=trailers"

# Test CORS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://82.25.79.43/get_videos
```

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check if the CDN service is running: `./vps-manager.sh status`
   - Check nginx logs: `./vps-manager.sh nginx-logs`
   - Restart the service: `./vps-manager.sh restart`

2. **CORS Errors**
   - Verify nginx configuration: `./vps-manager.sh nginx-test`
   - Reload nginx: `./vps-manager.sh nginx-reload`

3. **Service Not Responding**
   - Check PM2 status: `pm2 status`
   - View logs: `./vps-manager.sh logs`
   - Check environment variables: `cat /opt/tnoradio-cdn-service/.env`

### Debugging Steps

1. **Check Service Status**
   ```bash
   ./vps-manager.sh status
   ```

2. **View Recent Logs**
   ```bash
   ./vps-manager.sh logs
   ```

3. **Test Endpoints**
   ```bash
   ./vps-manager.sh test-endpoints
   ```

4. **Monitor in Real-time**
   ```bash
   ./vps-manager.sh monitor
   ```

## Backup and Recovery

### Create Backup

```bash
./vps-manager.sh backup-config
```

### Restore from Backup

```bash
./vps-manager.sh restore-config
```

## Security Considerations

1. **Environment Variables**: Keep API keys secure and never commit them to version control
2. **Firewall**: Ensure only necessary ports are open (80, 443, 22)
3. **SSL**: Consider adding SSL certificates for HTTPS
4. **Updates**: Keep the system and dependencies updated

## Monitoring

### Health Checks

The service provides health check endpoints:

- `http://82.25.79.43/health` - Basic health check
- `http://82.25.79.43:19000/health` - Direct service health check

### Logs

- PM2 logs: `pm2 logs cdn`
- Nginx access logs: `/var/log/nginx/access.log`
- Nginx error logs: `/var/log/nginx/error.log`
- Application logs: `/opt/tnoradio-cdn-service/cdn.log`

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Use the VPS management script to diagnose issues
3. Check the logs for error messages
4. Verify the configuration files

## Files Structure

```
/opt/tnoradio-cdn-service/
├── app.py                 # Main Flask application
├── stream.py             # BunnyCDN stream integration
├── storage.py            # BunnyCDN storage integration
├── requirements.txt      # Python dependencies
├── ecosystem.config.js   # PM2 configuration
├── .env                  # Environment variables
└── cdn.log              # Application logs
```

## Updates

To update the service:

1. Push changes to the repository
2. Jenkins will automatically deploy
3. Or use manual deployment steps above
4. Test the endpoints after deployment 