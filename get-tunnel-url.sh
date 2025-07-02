#!/bin/bash

# Get Tunnel URL Script
# This script helps get the localtunnel URL for GitHub webhook setup

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

print_header "Getting Tunnel URL for GitHub Webhook"
echo ""

# Check if localtunnel is running
if ! pgrep -f "localtunnel.*8080" > /dev/null; then
    print_warning "localtunnel is not running on port 8080"
    print_status "Starting localtunnel..."
    npx localtunnel --port 8080 > /tmp/localtunnel.log 2>&1 &
    sleep 5
fi

# Try to get the URL from the log
if [ -f /tmp/localtunnel.log ]; then
    TUNNEL_URL=$(grep -o 'https://[a-zA-Z0-9-]*\.loca\.lt' /tmp/localtunnel.log | tail -1)
fi

# If not found in log, try alternative method
if [ -z "$TUNNEL_URL" ]; then
    print_warning "Could not find URL in log, trying alternative method..."
    
    # Try to get from localtunnel API
    TUNNEL_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*' | head -1)
fi

# If still not found, provide instructions
if [ -z "$TUNNEL_URL" ]; then
    print_warning "Could not automatically detect tunnel URL"
    echo ""
    print_header "Manual Setup Instructions:"
    echo "1. Check your terminal where localtunnel is running"
    echo "2. Look for a line like: 'your url is: https://abc123.loca.lt'"
    echo "3. Use that URL for your webhook"
    echo ""
    print_status "Expected webhook URL format:"
    echo "https://YOUR_SUBDOMAIN.loca.lt/generic-webhook-trigger/invoke"
    echo ""
    
    # Show localtunnel log
    if [ -f /tmp/localtunnel.log ]; then
        print_header "Recent localtunnel output:"
        tail -10 /tmp/localtunnel.log
    fi
else
    print_status "✅ Tunnel URL found!"
    echo ""
    print_header "Your Jenkins Public URL:"
    echo "${TUNNEL_URL}"
    echo ""
    print_header "GitHub Webhook Payload URL:"
    echo "${TUNNEL_URL}/generic-webhook-trigger/invoke"
    echo ""
    
    # Save URLs to files
    echo "${TUNNEL_URL}" > .tunnel-url
    echo "${TUNNEL_URL}/generic-webhook-trigger/invoke" > .webhook-url
    
    print_status "URLs saved to .tunnel-url and .webhook-url"
    echo ""
    
    print_header "Next Steps:"
    echo "1. Copy the webhook URL above"
    echo "2. Go to: https://github.com/karolscript/tnoradio-cdn-service/settings/hooks"
    echo "3. Click 'Add webhook'"
    echo "4. Configure:"
    echo "   - Payload URL: ${TUNNEL_URL}/generic-webhook-trigger/invoke"
    echo "   - Content type: application/json"
    echo "   - Events: Just the push event"
    echo "5. Click 'Add webhook'"
    echo ""
    
    print_warning "⚠️  Keep localtunnel running to maintain the tunnel"
    print_warning "The URL will change if you restart localtunnel"
fi

echo ""
print_header "Testing the tunnel..."
if [ -n "$TUNNEL_URL" ]; then
    if curl -s "${TUNNEL_URL}" > /dev/null 2>&1; then
        print_status "✅ Tunnel is working!"
    else
        print_warning "⚠️  Tunnel might not be ready yet, wait a moment and try again"
    fi
fi 