#!/bin/bash

# ngrok Setup Script for Local Jenkins
# This script helps set up ngrok to expose your local Jenkins to GitHub webhooks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Configuration
JENKINS_PORT="8080"
NGROK_CONFIG_DIR="$HOME/.ngrok2"

print_header "ngrok Setup for Local Jenkins"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    print_error "ngrok is not installed"
    print_warning "Install ngrok first:"
    echo "   brew install ngrok/ngrok/ngrok"
    exit 1
fi

print_status "✅ ngrok is installed"

# Check if Jenkins is running
print_header "1. Checking Jenkins Status"
if curl -s http://localhost:${JENKINS_PORT} > /dev/null 2>&1; then
    print_status "✅ Jenkins is running on localhost:${JENKINS_PORT}"
else
    print_error "❌ Jenkins is not running on localhost:${JENKINS_PORT}"
    print_warning "Start Jenkins first, then run this script again"
    exit 1
fi

# Check ngrok authentication
print_header "2. Checking ngrok Authentication"
if [ -f "$NGROK_CONFIG_DIR/ngrok.yml" ]; then
    print_status "✅ ngrok config found"
else
    print_warning "⚠️  ngrok not authenticated"
    echo ""
    echo "To authenticate ngrok:"
    echo "1. Go to https://ngrok.com/signup"
    echo "2. Create a free account"
    echo "3. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "4. Run: ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    read -p "Do you want to continue without authentication? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start ngrok tunnel
print_header "3. Starting ngrok Tunnel"
echo ""
print_status "Starting ngrok tunnel to localhost:${JENKINS_PORT}..."
echo "This will create a public URL for your local Jenkins"
echo ""

# Start ngrok in background
ngrok http ${JENKINS_PORT} > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

# Wait a moment for ngrok to start
sleep 3

# Get the public URL
if [ -f /tmp/ngrok.log ]; then
    NGROK_URL=$(grep -o 'https://[a-zA-Z0-9]*\.ngrok\.io' /tmp/ngrok.log | head -1)
    if [ -n "$NGROK_URL" ]; then
        print_status "✅ ngrok tunnel started successfully"
        echo ""
        print_header "Your Jenkins Public URL:"
        echo "${NGROK_URL}"
        echo ""
        print_header "GitHub Webhook Payload URL:"
        echo "${NGROK_URL}/generic-webhook-trigger/invoke"
        echo ""
        
        # Save the URL to a file for easy access
        echo "${NGROK_URL}" > .ngrok-url
        echo "${NGROK_URL}/generic-webhook-trigger/invoke" > .webhook-url
        
        print_status "URLs saved to .ngrok-url and .webhook-url"
        echo ""
        
        print_header "Next Steps:"
        echo "1. Copy the webhook URL above"
        echo "2. Go to your GitHub repository: https://github.com/karolscript/tnoradio-cdn-service"
        echo "3. Settings → Webhooks → Add webhook"
        echo "4. Use the webhook URL as Payload URL"
        echo "5. Content type: application/json"
        echo "6. Events: Just the push event"
        echo ""
        
        print_warning "⚠️  Keep this terminal open to maintain the tunnel"
        print_warning "Press Ctrl+C to stop the tunnel when done"
        echo ""
        
        # Show ngrok status
        print_header "ngrok Status:"
        curl -s http://localhost:4040/api/tunnels | python3 -m json.tool 2>/dev/null || echo "ngrok status not available"
        echo ""
        
        # Wait for user to stop
        print_status "Tunnel is running. Press Ctrl+C to stop..."
        wait $NGROK_PID
        
    else
        print_error "❌ Failed to get ngrok URL"
        print_warning "Check /tmp/ngrok.log for details"
        kill $NGROK_PID 2>/dev/null || true
        exit 1
    fi
else
    print_error "❌ Failed to start ngrok"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

# Cleanup
cleanup() {
    print_status "Stopping ngrok tunnel..."
    kill $NGROK_PID 2>/dev/null || true
    rm -f /tmp/ngrok.log
    print_status "Tunnel stopped"
}

trap cleanup EXIT 