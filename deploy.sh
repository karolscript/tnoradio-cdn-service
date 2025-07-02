#!/bin/bash

# CDN Service Deployment Script
# This script restarts the CDN service and updates nginx configuration

set -e

echo "🚀 Starting CDN Service Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root (for nginx operations)
if [[ $EUID -eq 0 ]]; then
    print_status "Running as root - nginx operations will be available"
else
    print_warning "Not running as root - nginx operations may fail"
fi

# Stop existing CDN service if running
print_status "Stopping existing CDN service..."
if command -v pm2 &> /dev/null; then
    pm2 stop cdn 2>/dev/null || print_warning "CDN service not running in PM2"
    pm2 delete cdn 2>/dev/null || print_warning "CDN service not found in PM2"
fi

# Kill any existing processes on port 19000
print_status "Checking for processes on port 19000..."
if lsof -ti:19000 > /dev/null 2>&1; then
    print_warning "Found processes on port 19000, killing them..."
    lsof -ti:19000 | xargs kill -9
fi

# Install/update dependencies
print_status "Installing Python dependencies..."
pip3 install -r requirements.txt

# Start the CDN service
print_status "Starting CDN service..."
if command -v pm2 &> /dev/null; then
    pm2 start ecosystem.config.js
    pm2 save
    print_status "CDN service started with PM2"
else
    print_warning "PM2 not found, starting service directly..."
    nohup python3 app.py > cdn.log 2>&1 &
    echo $! > cdn.pid
    print_status "CDN service started directly (PID: $(cat cdn.pid))"
fi

# Wait for service to start
print_status "Waiting for service to start..."
sleep 5

# Test the service
print_status "Testing CDN service..."
if curl -s http://localhost:19000/health > /dev/null; then
    print_status "✅ CDN service is responding"
else
    print_error "❌ CDN service is not responding"
    exit 1
fi

# Update nginx configuration if running as root
if [[ $EUID -eq 0 ]]; then
    print_status "Updating nginx configuration..."
    
    # Backup existing nginx config
    if [ -f /etc/nginx/nginx.conf ]; then
        cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)
        print_status "Backed up existing nginx configuration"
    fi
    
    # Copy new nginx config
    cp nginx.conf /etc/nginx/nginx.conf
    
    # Test nginx configuration
    if nginx -t; then
        print_status "✅ Nginx configuration is valid"
        
        # Reload nginx
        systemctl reload nginx
        print_status "✅ Nginx reloaded successfully"
    else
        print_error "❌ Nginx configuration is invalid"
        exit 1
    fi
else
    print_warning "Skipping nginx configuration update (not running as root)"
fi

# Run tests
print_status "Running service tests..."
if [ -f test_cdn.py ]; then
    python3 test_cdn.py
else
    print_warning "Test script not found, skipping tests"
fi

print_status "🎉 Deployment completed successfully!"

# Show service status
print_status "Service Status:"
if command -v pm2 &> /dev/null; then
    pm2 status
else
    if [ -f cdn.pid ]; then
        echo "CDN service PID: $(cat cdn.pid)"
        if ps -p $(cat cdn.pid) > /dev/null; then
            print_status "✅ Service is running"
        else
            print_error "❌ Service is not running"
        fi
    fi
fi

print_status "Service URL: http://localhost:19000"
print_status "Health check: http://localhost:19000/health"
print_status "Test endpoint: http://localhost:19000/get_videos?collection=trailers" 