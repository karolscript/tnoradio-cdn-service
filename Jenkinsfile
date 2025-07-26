pipeline {
  agent any
  environment {
    VPS_USER = 'root'
    VPS_IP = '82.25.79.43'
    APP_DIR = '/opt/tnoradio-cdn-service'
    SERVICE_PORT = '19000'
    PM2_APP_NAME = 'cdn'
    NODE_ENV = 'production'
  }
  
  triggers {
    GenericTrigger(
      genericVariables: [
        [key: 'ref', value: '$.push.changes[0].new.name']
      ],
      token: 'jenkins-webhook-lechuzas-cdn',  
      causeString: 'Triggered by Bitbucket push',
      printContributedVariables: true,
      printPostContent: true
    )
  }
  
  stages {
    stage('Checkout') {
      steps {
        script {
          echo "Starting deployment for repository: tnoradio-cdn-service"
          echo "Branch: main"
        }
        git(
          branch: 'main',
          url: 'https://karolscript@bitbucket.org/tnoradio/tnoradio-cdn-service.git',
          credentialsId: 'bitbucket-app-pass'
        )
      }
    }
    
    stage('Validate') {
      steps {
        script {
          echo "Validating deployment configuration..."
          sh 'ls -la'
          sh 'cat requirements.txt | head -10'
        }
      }
    }
    
    stage('Deploy') {
      steps {
        sshagent(credentials: ['ssh-tnonetwork']) {
          script {
            echo "Deploying to VPS: ${VPS_IP}"
            echo "Target directory: ${APP_DIR}"
            
            // Sync files first (excluding venv, .git, .env, and __pycache__)
            sh """
              rsync -avz --delete --exclude='.git' --exclude='venv' --exclude='.env' --exclude='__pycache__' --exclude='*.pyc' . ${VPS_USER}@${VPS_IP}:${APP_DIR}
            """
            
            // Create backup on the VPS
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'cp -r ${APP_DIR} ${APP_DIR}-backup-\$(date +%Y%m%d-%H%M%S) 2>/dev/null || true'
            """
            
            // Set correct permissions
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'chown -R ${VPS_USER}:${VPS_USER} ${APP_DIR}'
            """
            
            // Install PM2 globally if not already installed
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'npm install -g pm2 2>/dev/null || true'
            """
            
            // Set up Python virtual environment and install dependencies
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'cd ${APP_DIR} && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt'
            """

            // Copy .env file if it doesn't exist (preserve existing one)
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'if [ ! -f ${APP_DIR}/.env ]; then cat > ${APP_DIR}/.env << EOF
BUNNY_STORAGE_API_KEY=your_bunny_storage_api_key_here
BUNNY_API_KEY=your_bunny_api_key_here
BUNNY_VIDEO_LIBRARY_ID=286671
EOF
echo ".env file created, please update with actual API keys"; fi'
            """
            
            // Restart the service with PM2
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'source /root/.nvm/nvm.sh && cd ${APP_DIR} && pm2 restart ${PM2_APP_NAME} || (pm2 start ecosystem.config.js --env production)'
            """
            
            echo "Deployment completed successfully!"
          }
        }
      }
      post {
        success {
          script {
            echo "✅ Deployment successful!"
            // Check PM2 status
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'source /root/.nvm/nvm.sh && pm2 status ${PM2_APP_NAME}'
            """
            // Check if service is responding
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'curl -s http://localhost:${SERVICE_PORT}/health || echo "Health check failed"'
            """
          }
        }
        failure {
          echo "❌ Deployment failed!"
          // Optionally add notification here (email, Slack, etc.)
        }
      }
    }
  }
  
  post {
    always {
      script {
        echo "Pipeline completed with status: ${currentBuild.result}"
        // Clean up old backups (keep last 5)
        sh """
          ssh ${VPS_USER}@${VPS_IP} 'cd ${APP_DIR} && ls -t ${APP_DIR}-backup-* | tail -n +6 | xargs rm -rf 2>/dev/null || true'
        """
      }
    }
  }
}
