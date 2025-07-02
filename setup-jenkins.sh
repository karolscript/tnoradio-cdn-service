#!/bin/bash

# Jenkins Setup Script for CDN Service
# This script helps set up the Jenkins job and GitHub webhook

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
JENKINS_URL=""
GITHUB_REPO=""
VPS_IP="82.25.79.43"

# Function to show usage
show_usage() {
    echo "Jenkins Setup Script for CDN Service"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -j, --jenkins-url URL    Jenkins server URL (e.g., http://jenkins:8080)"
    echo "  -g, --github-repo REPO   GitHub repository URL"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 -j http://jenkins:8080 -g https://github.com/username/TNONetwork"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -j|--jenkins-url)
            JENKINS_URL="$2"
            shift 2
            ;;
        -g|--github-repo)
            GITHUB_REPO="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$JENKINS_URL" || -z "$GITHUB_REPO" ]]; then
    print_error "Jenkins URL and GitHub repository are required"
    show_usage
    exit 1
fi

print_header "Jenkins Setup for CDN Service"
echo "Jenkins URL: $JENKINS_URL"
echo "GitHub Repo: $GITHUB_REPO"
echo "VPS IP: $VPS_IP"
echo ""

# Function to check if Jenkins is accessible
check_jenkins() {
    print_status "Checking Jenkins accessibility..."
    if curl -s "$JENKINS_URL" > /dev/null; then
        print_status "✅ Jenkins is accessible"
    else
        print_error "❌ Cannot access Jenkins at $JENKINS_URL"
        print_warning "Make sure Jenkins is running and accessible"
        exit 1
    fi
}

# Function to generate webhook URL
generate_webhook_url() {
    print_status "Generating webhook URL..."
    WEBHOOK_URL="$JENKINS_URL/generic-webhook-trigger/invoke"
    print_status "Webhook URL: $WEBHOOK_URL"
    echo ""
}

# Function to create GitHub webhook configuration
create_github_webhook_config() {
    print_header "GitHub Webhook Configuration"
    echo ""
    echo "Follow these steps to configure the GitHub webhook:"
    echo ""
    echo "1. Go to your GitHub repository: $GITHUB_REPO"
    echo "2. Click 'Settings' tab"
    echo "3. Click 'Webhooks' in the left sidebar"
    echo "4. Click 'Add webhook'"
    echo ""
    echo "Configure the webhook with these settings:"
    echo "  • Payload URL: $WEBHOOK_URL"
    echo "  • Content type: application/json"
    echo "  • Secret: (leave empty)"
    echo "  • Events: Just the push event"
    echo "  • Active: ✅ Checked"
    echo ""
    print_warning "After adding the webhook, test it with a push to your repository"
}

# Function to create Jenkins job configuration
create_jenkins_job_config() {
    print_header "Jenkins Job Configuration"
    echo ""
    echo "Follow these steps to create the Jenkins job:"
    echo ""
    echo "1. Go to Jenkins: $JENKINS_URL"
    echo "2. Click 'New Item'"
    echo "3. Enter job name: cdn-service-deploy"
    echo "4. Select 'Pipeline'"
    echo "5. Click 'OK'"
    echo ""
    echo "Configure the job with these settings:"
    echo ""
    echo "General:"
    echo "  • Description: CDN Service deployment pipeline for VPS ($VPS_IP)"
    echo "  • Discard old builds: ✅ Checked"
    echo "    - Days to keep builds: 30"
    echo "    - Max # of builds to keep: 50"
    echo ""
    echo "Build Triggers:"
    echo "  • Generic Webhook Trigger: ✅ Checked"
    echo "  • Token: jenkins-webhook-lechuzas-cdn"
    echo ""
    echo "Pipeline:"
    echo "  • Definition: Pipeline script from SCM"
    echo "  • SCM: Git"
    echo "  • Repository URL: $GITHUB_REPO"
    echo "  • Branch Specifier: */main"
    echo "  • Script Path: tnoradio-cdn-service/Jenkinsfile"
    echo ""
}

# Function to create SSH credentials guide
create_ssh_credentials_guide() {
    print_header "SSH Credentials Setup"
    echo ""
    echo "Set up SSH credentials for VPS access:"
    echo ""
    echo "1. Go to Jenkins: $JENKINS_URL"
    echo "2. Manage Jenkins → Manage Credentials"
    echo "3. System → Global credentials → Add Credentials"
    echo ""
    echo "Configure SSH credentials:"
    echo "  • Kind: SSH Username with private key"
    echo "  • Scope: Global"
    echo "  • ID: vps-ssh-key"
    echo "  • Description: VPS SSH Key for CDN Service"
    echo "  • Username: root"
    echo "  • Private Key: Enter your private key"
    echo "  • Passphrase: (if your key has one)"
    echo ""
}

# Function to create test script
create_test_script() {
    print_header "Testing the Setup"
    echo ""
    echo "After completing the setup, test it with these commands:"
    echo ""
    echo "1. Test SSH connection to VPS:"
    echo "   ssh root@$VPS_IP"
    echo ""
    echo "2. Test Jenkins webhook manually:"
    echo "   curl -X POST $WEBHOOK_URL \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"repository\":{\"name\":\"TNONetwork\"},\"ref\":\"refs/heads/main\"}'"
    echo ""
    echo "3. Test CDN service endpoints:"
    echo "   curl http://$VPS_IP/health"
    echo "   curl \"http://$VPS_IP/get_videos?collection=trailers\""
    echo ""
    echo "4. Use the VPS manager script:"
    echo "   ./vps-manager.sh status"
    echo "   ./vps-manager.sh test-endpoints"
    echo ""
}

# Function to create environment setup guide
create_environment_guide() {
    print_header "Environment Setup"
    echo ""
    echo "Make sure your VPS has the required software:"
    echo ""
    echo "1. Python 3.8+:"
    echo "   python3 --version"
    echo ""
    echo "2. PM2:"
    echo "   npm install -g pm2"
    echo ""
    echo "3. Nginx:"
    echo "   sudo apt update && sudo apt install nginx"
    echo ""
    echo "4. Required Python packages (will be installed by Jenkins):"
    echo "   pip3 install flask flask-cors requests python-dotenv"
    echo ""
}

# Main execution
main() {
    print_header "Starting Jenkins Setup for CDN Service"
    echo ""
    
    check_jenkins
    generate_webhook_url
    echo ""
    
    create_github_webhook_config
    echo ""
    
    create_jenkins_job_config
    echo ""
    
    create_ssh_credentials_guide
    echo ""
    
    create_environment_guide
    echo ""
    
    create_test_script
    echo ""
    
    print_header "Setup Complete!"
    echo ""
    echo "Next steps:"
    echo "1. Configure the GitHub webhook as shown above"
    echo "2. Create the Jenkins job as shown above"
    echo "3. Set up SSH credentials"
    echo "4. Test the complete pipeline"
    echo ""
    echo "For detailed instructions, see:"
    echo "  • JENKINS_SETUP_GUIDE.md"
    echo "  • DEPLOYMENT_GUIDE.md"
    echo "  • github-webhook-setup.md"
    echo ""
    print_status "🎉 Setup guide generated successfully!"
}

# Run main function
main 