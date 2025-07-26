pipeline {
  agent any
  environment {
    VPS_USER = 'root'
    VPS_IP = '82.25.79.43'
    APP_DIR = '/home/api/tnoradio-cdn-service'
    SERVICE_PORT = '19000'
    APP_NAME = 'tnoradio-cdn-service'
    NODE_ENV = 'production'
  }
  
  triggers {
    GenericTrigger(
      genericVariables: [
        [key: 'ref', value: '$.push.changes[0].new.name']
      ],
      token: 'jenkins-webhook-lechuzas-cdn',  
      causeString: 'Triggered by github push',
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
          url: 'https://github.com/karolscript/tnoradio-cdn-service.git',
          credentialsId: 'ssh-tnonetwork'
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
              rsync -avz --delete --exclude='.git' --exclude='venv' --exclude='.env' --exclude='__pycache__' --exclude='*.pyc' --exclude='cdn.log' . ${VPS_USER}@${VPS_IP}:${APP_DIR}
            """
            
            // Create backup on the VPS
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'cp -r ${APP_DIR} ${APP_DIR}-backup-\$(date +%Y%m%d-%H%M%S) 2>/dev/null || true'
            """
            
            // Set correct permissions
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'chown -R ${VPS_USER}:${VPS_USER} ${APP_DIR}'
            """
            
            // Set up Python virtual environment and install dependencies
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'cd ${APP_DIR} && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt'
            """

            // Preserve existing .env file (don't overwrite it)
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'echo "Preserving existing .env file with API keys"'
            """
            
            // Stop existing gunicorn processes and restart the service
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'cd ${APP_DIR} && pkill -f gunicorn || true && sleep 2 && nohup ./venv/bin/python /usr/bin/gunicorn --bind 0.0.0.0:${SERVICE_PORT} --workers 2 --worker-class sync --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 app:app > cdn.log 2>&1 &'
            """
            
            echo "Deployment completed successfully!"
          }
        }
      }
      post {
        success {
          script {
            echo "✅ Deployment successful!"
            // Check if gunicorn processes are running
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'ps aux | grep gunicorn | grep -v grep || echo "No gunicorn processes found"'
            """
            // Check if service is responding
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'curl -s http://localhost:${SERVICE_PORT}/health || echo "Health check failed"'
            """
            // Check recent logs
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'cd ${APP_DIR} && tail -10 cdn.log || echo "No log file found"'
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
