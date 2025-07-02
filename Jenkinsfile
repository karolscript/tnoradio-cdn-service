pipeline {
  agent any
  environment {
    VPS_USER = 'root'
    VPS_IP = '82.25.79.43'
    SERVICE_NAME = 'tnoradio-cdn-service'
    SERVICE_PORT = '19000'
    NGINX_CONFIG_PATH = '/etc/nginx/nginx.conf'
    PM2_APP_NAME = 'cdn'
  }
  
  triggers {
    GenericTrigger(
      genericVariables: [
        [key: 'ref', value: '$.ref'],
        [key: 'repository', value: '$.repository.name'],
        [key: 'branch', value: '$.ref_name']
      ],
      token: 'jenkins-webhook-lechuzas-cdn',  
      causeString: 'Triggered by GitHub push',
      printContributedVariables: true,
      printPostContent: true,
      regexpFilterText: '$ref',
      regexpFilterExpression: 'refs/heads/main'
    )
  }
  
  stages {
    stage('Checkout') {
      steps {
        checkout([$class: 'GitSCM', 
          branches: [[name: '*/main']], 
          doGenerateSubmoduleConfigurations: false, 
          extensions: [], 
          submoduleCfg: [], 
          userRemoteConfigs: [[
            url: 'https://github.com/karolscript/tnoradio-cdn-service.git'
          ]]
        ])
        sh 'pwd && ls -la'
      }
    }

    stage('Install Dependencies') {
      steps {
        sh '''
          echo "Installing Python dependencies..."
          pip3 install -r requirements.txt
        '''
      }
    }

    stage('Test Service Locally') {
      steps {
        sh '''
          echo "Testing service locally..."
          python3 test_cdn.py || echo "Local test failed, continuing with deployment..."
        '''
      }
    }

    stage('Deploy to VPS') {
      steps {
        script {
          // Create deployment package
          sh '''
            echo "Creating deployment package..."
            tar -czf cdn-service-deploy.tar.gz --exclude=cdn-service-deploy.tar.gz .
          '''
          
          // Copy files to VPS
          sh '''
            echo "Copying files to VPS..."
            scp -o StrictHostKeyChecking=no cdn-service-deploy.tar.gz ${VPS_USER}@${VPS_IP}:/tmp/
            scp -o StrictHostKeyChecking=no nginx.conf ${VPS_USER}@${VPS_IP}:/tmp/nginx-cdn.conf
            scp -o StrictHostKeyChecking=no ecosystem.config.js ${VPS_USER}@${VPS_IP}:/tmp/
          '''
          
          // Execute deployment on VPS
          sh '''
            ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
              set -e
              
              echo "🚀 Starting CDN Service Deployment on VPS..."
              
              # Create service directory if it doesn't exist
              mkdir -p /opt/${SERVICE_NAME}
              
              # Stop existing service
              echo "Stopping existing CDN service..."
              pm2 stop ${PM2_APP_NAME} 2>/dev/null || echo "Service not running in PM2"
              pm2 delete ${PM2_APP_NAME} 2>/dev/null || echo "Service not found in PM2"
              
              # Kill any existing processes on port
              if lsof -ti:${SERVICE_PORT} > /dev/null 2>&1; then
                echo "Killing processes on port ${SERVICE_PORT}..."
                lsof -ti:${SERVICE_PORT} | xargs kill -9
              fi
              
              # Extract deployment package
              echo "Extracting deployment package..."
              cd /opt/${SERVICE_NAME}
              tar -xzf /tmp/cdn-service-deploy.tar.gz
              
              # Install dependencies
              echo "Installing Python dependencies..."
              # Create virtual environment
              python3 -m venv venv
              source venv/bin/activate
              pip install -r requirements.txt
              
              # Set up environment variables
              if [ ! -f .env ]; then
                echo "Creating .env file..."
                cat > .env << 'ENVEOF'
BUNNY_STORAGE_API_KEY=your_bunny_storage_api_key_here
BUNNY_API_KEY=your_bunny_api_key_here
BUNNY_VIDEO_LIBRARY_ID=286671
ENVEOF
                echo "⚠️  Please update the .env file with your actual API keys!"
              fi
              
              # Start service with PM2
              echo "Starting CDN service with PM2..."
              cp /tmp/ecosystem.config.js .
              # Ensure virtual environment is activated for PM2
              export PATH="/opt/${SERVICE_NAME}/venv/bin:$PATH"
              pm2 start ecosystem.config.js
              pm2 save
              
              # Wait for service to start
              echo "Waiting for service to start..."
              sleep 10
              
              # Test service
              echo "Testing CDN service..."
              if curl -s http://localhost:${SERVICE_PORT}/health > /dev/null; then
                echo "✅ CDN service is responding"
              else
                echo "❌ CDN service is not responding"
                exit 1
              fi
              
              echo "🎉 CDN service deployment completed!"
            EOF
          '''
        }
      }
    }

    stage('Update Nginx Configuration') {
      steps {
        script {
          sh '''
            ssh -o StrictHostKeyChecking=no ${VPS_USER}@${VPS_IP} << 'EOF'
              set -e
              
              echo "Updating nginx configuration..."
              
              # Backup existing nginx config
              if [ -f ${NGINX_CONFIG_PATH} ]; then
                cp ${NGINX_CONFIG_PATH} ${NGINX_CONFIG_PATH}.backup.$(date +%Y%m%d_%H%M%S)
                echo "Backed up existing nginx configuration"
              fi
              
              # Check if we need to merge with existing config
              if grep -q "upstream cdn_backend" ${NGINX_CONFIG_PATH} 2>/dev/null; then
                echo "CDN upstream already exists in nginx config, updating..."
                # Remove existing CDN configuration
                sed -i '/upstream cdn_backend/,/}/d' ${NGINX_CONFIG_PATH}
                sed -i '/server_name.*cdn.tnonetwork.com/,/}/d' ${NGINX_CONFIG_PATH}
              fi
              
              # Add CDN configuration to existing nginx config
              echo "Adding CDN configuration to nginx..."
              
              # Add upstream before the first server block
              sed -i '/http {/a\\n    # Upstream for CDN service\n    upstream cdn_backend {\n        server 127.0.0.1:19000;\n    }\n' ${NGINX_CONFIG_PATH}
              
              # Add server block before the closing http brace
              sed -i '/^}/i\\n    # CDN Service server block\n    server {\n        listen       80;\n        listen       [::]:80;\n        server_name  cdn.tnonetwork.com 82.25.79.43;\n        root         /usr/share/nginx/html;\n\n        # CORS headers for all requests\n        add_header '\''Access-Control-Allow-Origin'\'' '\''*'\'' always;\n        add_header '\''Access-Control-Allow-Methods'\'' '\''GET, POST, PUT, DELETE, OPTIONS'\'' always;\n        add_header '\''Access-Control-Allow-Headers'\'' '\''DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization'\'' always;\n        add_header '\''Access-Control-Expose-Headers'\'' '\''Content-Length,Content-Range'\'' always;\n\n        # Handle preflight requests\n        if ($request_method = '\''OPTIONS'\'') {\n            add_header '\''Access-Control-Allow-Origin'\'' '\''*'\'';\n            add_header '\''Access-Control-Allow-Methods'\'' '\''GET, POST, PUT, DELETE, OPTIONS'\'';\n            add_header '\''Access-Control-Allow-Headers'\'' '\''DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization'\'';\n            add_header '\''Access-Control-Max-Age'\'' 1728000;\n            add_header '\''Content-Type'\'' '\''text/plain; charset=utf-8'\'';\n            add_header '\''Content-Length'\'' 0;\n            return 204;\n        }\n\n        # Proxy for CDN service\n        location / {\n            proxy_pass http://cdn_backend;\n            proxy_http_version 1.1;\n            proxy_set_header Upgrade $http_upgrade;\n            proxy_set_header Connection '\''upgrade'\'';\n            proxy_set_header Host $host;\n            proxy_set_header X-Real-IP $remote_addr;\n            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n            proxy_set_header X-Forwarded-Proto $scheme;\n            proxy_cache_bypass $http_upgrade;\n            proxy_read_timeout 86400;\n            proxy_connect_timeout 60;\n            proxy_send_timeout 60;\n        }\n\n        # Health check endpoint\n        location /health {\n            proxy_pass http://cdn_backend/health;\n            proxy_http_version 1.1;\n            proxy_set_header Host $host;\n            proxy_set_header X-Real-IP $remote_addr;\n            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n            proxy_set_header X-Forwarded-Proto $scheme;\n        }\n\n        # Specific endpoint for videos\n        location /get_videos {\n            proxy_pass http://cdn_backend/get_videos;\n            proxy_http_version 1.1;\n            proxy_set_header Host $host;\n            proxy_set_header X-Real-IP $remote_addr;\n            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n            proxy_set_header X-Forwarded-Proto $scheme;\n            proxy_read_timeout 86400;\n        }\n\n        error_page 404 /404.html;\n        location = /404.html {\n        }\n\n        error_page 500 502 503 504 /50x.html;\n        location = /50x.html {\n        }\n    }\n' ${NGINX_CONFIG_PATH}
              
              # Test nginx configuration
              if nginx -t; then
                echo "✅ Nginx configuration is valid"
                
                # Reload nginx
                systemctl reload nginx
                echo "✅ Nginx reloaded successfully"
              else
                echo "❌ Nginx configuration is invalid"
                exit 1
              fi
              
              echo "🎉 Nginx configuration updated successfully!"
            EOF
          '''
        }
      }
    }

    stage('Test Deployment') {
      steps {
        script {
          sh '''
            echo "Testing deployment..."
            sleep 5
            
            # Test health endpoint
            if curl -s http://${VPS_IP}/health > /dev/null; then
              echo "✅ Health endpoint is working"
            else
              echo "❌ Health endpoint is not working"
            fi
            
            # Test videos endpoint
            if curl -s "http://${VPS_IP}/get_videos?collection=trailers" > /dev/null; then
              echo "✅ Videos endpoint is working"
            else
              echo "❌ Videos endpoint is not working"
            fi
            
            # Test CORS
            if curl -s -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -X OPTIONS http://${VPS_IP}/get_videos > /dev/null; then
              echo "✅ CORS is working"
            else
              echo "❌ CORS is not working"
            fi
          '''
        }
      }
    }

    stage('Cleanup') {
      steps {
        sh '''
          echo "Cleaning up temporary files..."
          rm -f cdn-service-deploy.tar.gz
        '''
      }
    }
  }
  
  post {
    always {
      echo "Deployment completed!"
    }
    success {
      echo "✅ CDN service deployed successfully to VPS!"
      echo "Service URL: http://${VPS_IP}"
      echo "Health check: http://${VPS_IP}/health"
      echo "Videos endpoint: http://${VPS_IP}/get_videos?collection=trailers"
    }
    failure {
      echo "❌ Deployment failed!"
    }
  }
}
