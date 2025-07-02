#!/bin/bash

# VPS Management Script for CDN Service
# This script helps manage the CDN service on your VPS

set -e

# Configuration
VPS_IP="82.25.79.43"
VPS_USER="root"  # Change this to your VPS user
SERVICE_NAME="tnoradio-cdn-service"
SERVICE_PORT="19000"
SERVICE_DIR="/opt/${SERVICE_NAME}"

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

# Function to show usage
show_usage() {
    echo "VPS Management Script for CDN Service"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  connect          - Connect to VPS via SSH"
    echo "  status           - Check service status"
    echo "  logs             - View service logs"
    echo "  restart          - Restart CDN service"
    echo "  stop             - Stop CDN service"
    echo "  start            - Start CDN service"
    echo "  nginx-status     - Check nginx status"
    echo "  nginx-reload     - Reload nginx configuration"
    echo "  nginx-test       - Test nginx configuration"
    echo "  nginx-logs       - View nginx logs"
    echo "  test-endpoints   - Test CDN endpoints"
    echo "  update-env       - Update environment variables"
    echo "  backup-config    - Backup current configuration"
    echo "  restore-config   - Restore configuration from backup"
    echo "  monitor          - Monitor service in real-time"
    echo "  help             - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 connect"
    echo "  $0 status"
    echo "  $0 logs"
    echo "  $0 test-endpoints"
}

# Function to connect to VPS
connect_to_vps() {
    print_status "Connecting to VPS at ${VPS_IP}..."
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP}
}

# Function to check service status
check_service_status() {
    print_header "Checking CDN Service Status"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        echo "=== PM2 Status ==="
        pm2 status
        
        echo ""
        echo "=== Service Directory ==="
        ls -la /opt/tnoradio-cdn-service/
        
        echo ""
        echo "=== Process Status ==="
        ps aux | grep -E "(python|app.py)" | grep -v grep || echo "No Python processes found"
        
        echo ""
        echo "=== Port Status ==="
        netstat -tlnp | grep :19000 || echo "Port 19000 not listening"
        
        echo ""
        echo "=== Environment File ==="
        if [ -f /opt/tnoradio-cdn-service/.env ]; then
            echo "Environment file exists"
            cat /opt/tnoradio-cdn-service/.env | grep -v "API_KEY" | head -5
        else
            echo "Environment file not found"
        fi
EOF
}

# Function to view service logs
view_service_logs() {
    print_header "Viewing CDN Service Logs"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        echo "=== PM2 Logs ==="
        pm2 logs cdn --lines 50
        
        echo ""
        echo "=== Application Logs ==="
        if [ -f /opt/tnoradio-cdn-service/cdn.log ]; then
            tail -50 /opt/tnoradio-cdn-service/cdn.log
        else
            echo "No application log file found"
        fi
EOF
}

# Function to restart service
restart_service() {
    print_header "Restarting CDN Service"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        echo "Stopping CDN service..."
        pm2 stop cdn 2>/dev/null || echo "Service not running"
        pm2 delete cdn 2>/dev/null || echo "Service not found"
        
        echo "Starting CDN service..."
        cd /opt/tnoradio-cdn-service
        pm2 start ecosystem.config.js
        pm2 save
        
        echo "Waiting for service to start..."
        sleep 5
        
        echo "Testing service..."
        if curl -s http://localhost:19000/health > /dev/null; then
            echo "✅ Service is responding"
        else
            echo "❌ Service is not responding"
        fi
EOF
}

# Function to stop service
stop_service() {
    print_header "Stopping CDN Service"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        pm2 stop cdn
        pm2 delete cdn
        pm2 save
        echo "Service stopped"
EOF
}

# Function to start service
start_service() {
    print_header "Starting CDN Service"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        cd /opt/tnoradio-cdn-service
        pm2 start ecosystem.config.js
        pm2 save
        echo "Service started"
EOF
}

# Function to check nginx status
check_nginx_status() {
    print_header "Checking Nginx Status"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        echo "=== Nginx Status ==="
        systemctl status nginx --no-pager -l
        
        echo ""
        echo "=== Nginx Configuration ==="
        nginx -t
        
        echo ""
        echo "=== Nginx Processes ==="
        ps aux | grep nginx | grep -v grep
EOF
}

# Function to reload nginx
reload_nginx() {
    print_header "Reloading Nginx Configuration"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        nginx -t && systemctl reload nginx
        echo "Nginx reloaded successfully"
EOF
}

# Function to test nginx configuration
test_nginx_config() {
    print_header "Testing Nginx Configuration"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        nginx -t
EOF
}

# Function to view nginx logs
view_nginx_logs() {
    print_header "Viewing Nginx Logs"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        echo "=== Access Logs ==="
        tail -50 /var/log/nginx/access.log
        
        echo ""
        echo "=== Error Logs ==="
        tail -50 /var/log/nginx/error.log
EOF
}

# Function to test endpoints
test_endpoints() {
    print_header "Testing CDN Endpoints"
    
    echo "Testing health endpoint..."
    if curl -s http://${VPS_IP}/health > /dev/null; then
        print_status "✅ Health endpoint is working"
    else
        print_error "❌ Health endpoint is not working"
    fi
    
    echo "Testing videos endpoint..."
    if curl -s "http://${VPS_IP}/get_videos?collection=trailers" > /dev/null; then
        print_status "✅ Videos endpoint is working"
    else
        print_error "❌ Videos endpoint is not working"
    fi
    
    echo "Testing CORS..."
    if curl -s -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -X OPTIONS http://${VPS_IP}/get_videos > /dev/null; then
        print_status "✅ CORS is working"
    else
        print_error "❌ CORS is not working"
    fi
    
    echo "Testing direct service..."
    if curl -s http://${VPS_IP}:19000/health > /dev/null; then
        print_status "✅ Direct service is working"
    else
        print_error "❌ Direct service is not working"
    fi
}

# Function to update environment variables
update_env() {
    print_header "Updating Environment Variables"
    echo "Please enter the new environment variables:"
    read -p "BUNNY_STORAGE_API_KEY: " BUNNY_STORAGE_API_KEY
    read -p "BUNNY_API_KEY: " BUNNY_API_KEY
    read -p "BUNNY_VIDEO_LIBRARY_ID [286671]: " BUNNY_VIDEO_LIBRARY_ID
    BUNNY_VIDEO_LIBRARY_ID=${BUNNY_VIDEO_LIBRARY_ID:-286671}
    
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << EOF
        cd /opt/tnoradio-cdn-service
        cat > .env << 'ENVEOF'
BUNNY_STORAGE_API_KEY=${BUNNY_STORAGE_API_KEY}
BUNNY_API_KEY=${BUNNY_API_KEY}
BUNNY_VIDEO_LIBRARY_ID=${BUNNY_VIDEO_LIBRARY_ID}
ENVEOF
        echo "Environment variables updated"
        echo "Restarting service..."
        pm2 restart cdn
EOF
}

# Function to backup configuration
backup_config() {
    print_header "Backing Up Configuration"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        BACKUP_DIR="/opt/backups/cdn-service-$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR
        
        # Backup service files
        cp -r /opt/tnoradio-cdn-service $BACKUP_DIR/
        
        # Backup nginx config
        cp /etc/nginx/nginx.conf $BACKUP_DIR/
        
        # Backup PM2 config
        pm2 save
        cp ~/.pm2/dump.pm2 $BACKUP_DIR/
        
        echo "Backup created at: $BACKUP_DIR"
EOF
}

# Function to restore configuration
restore_config() {
    print_header "Restoring Configuration"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        echo "Available backups:"
        ls -la /opt/backups/
        
        read -p "Enter backup directory name: " BACKUP_DIR
        if [ -d "/opt/backups/$BACKUP_DIR" ]; then
            echo "Restoring from /opt/backups/$BACKUP_DIR"
            cp -r /opt/backups/$BACKUP_DIR/tnoradio-cdn-service/* /opt/tnoradio-cdn-service/
            cp /opt/backups/$BACKUP_DIR/nginx.conf /etc/nginx/
            cp /opt/backups/$BACKUP_DIR/dump.pm2 ~/.pm2/
            pm2 resurrect
            nginx -t && systemctl reload nginx
            echo "Configuration restored"
        else
            echo "Backup directory not found"
        fi
EOF
}

# Function to monitor service
monitor_service() {
    print_header "Monitoring CDN Service (Press Ctrl+C to stop)"
    ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
        watch -n 2 'echo "=== PM2 Status ==="; pm2 status; echo ""; echo "=== Port Status ==="; netstat -tlnp | grep :19000; echo ""; echo "=== Recent Logs ==="; pm2 logs cdn --lines 5 --nostream'
EOF
}

# Main script logic
case "$1" in
    connect)
        connect_to_vps
        ;;
    status)
        check_service_status
        ;;
    logs)
        view_service_logs
        ;;
    restart)
        restart_service
        ;;
    stop)
        stop_service
        ;;
    start)
        start_service
        ;;
    nginx-status)
        check_nginx_status
        ;;
    nginx-reload)
        reload_nginx
        ;;
    nginx-test)
        test_nginx_config
        ;;
    nginx-logs)
        view_nginx_logs
        ;;
    test-endpoints)
        test_endpoints
        ;;
    update-env)
        update_env
        ;;
    backup-config)
        backup_config
        ;;
    restore-config)
        restore_config
        ;;
    monitor)
        monitor_service
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac 