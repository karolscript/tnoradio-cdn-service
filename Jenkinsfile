pipeline {
  agent any
  options {
    timeout(time: 10, unit: 'MINUTES')
    retry(1)
  }
  environment {
    VPS_USER = 'root'
    VPS_IP = '82.25.79.43'
    APP_DIR = '/home/api/tnoradio-cdn-service'
    SERVICE_PORT = '19000'
    APP_NAME = 'tnoradio-cdn-service'
    NODE_ENV = 'production'
    DEPLOYMENT_TIMEOUT = '300'
    HEALTH_CHECK_RETRIES = '3'
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
          
          // Validate critical files exist
          sh '''
            echo "Validating critical files..."
            [ -f "app.py" ] || { echo "ERROR: app.py not found"; exit 1; }
            [ -f "storage.py" ] || { echo "ERROR: storage.py not found"; exit 1; }
            [ -f "youtube.py" ] || { echo "ERROR: youtube.py not found"; exit 1; }
            [ -f "requirements.txt" ] || { echo "ERROR: requirements.txt not found"; exit 1; }
            echo "✅ All critical files validated"
          '''
        }
      }
    }
    
    stage('Test') {
      steps {
        script {
          echo "Running basic tests..."
          sh '''
            echo "Testing Python syntax..."
            python3 -m py_compile app.py || { echo "ERROR: app.py has syntax errors"; exit 1; }
            python3 -m py_compile storage.py || { echo "ERROR: storage.py has syntax errors"; exit 1; }
            python3 -m py_compile youtube.py || { echo "ERROR: youtube.py has syntax errors"; exit 1; }
            echo "✅ All Python files compiled successfully"
          '''
        }
      }
    }
    
    stage('Deploy') {
      steps {
        sshagent(credentials: ['ssh-tnonetwork']) {
          script {
            echo "Deploying to VPS: ${VPS_IP}"
            echo "Target directory: ${APP_DIR}"
            
            // Copy only essential Python files
            sh """
              scp app.py storage.py youtube.py config.py requirements.txt ${VPS_USER}@${VPS_IP}:${APP_DIR}/
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
              ssh ${VPS_USER}@${VPS_IP} 'cd ${APP_DIR} && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && echo "Dependencies installed successfully"' || { echo "ERROR: Failed to install dependencies"; exit 1; }
            """

            // Preserve existing .env file (don't overwrite it)
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'echo "Preserving existing .env file with API keys"'
            """
            
            // Verify critical files were copied
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'cd ${APP_DIR} && echo "Verifying critical files:" && ls -la app.py storage.py youtube.py config.py requirements.txt || echo "Some critical files are missing!"'
            """
            
            // Stop existing gunicorn processes and restart the service
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'cd ${APP_DIR} && pkill -f gunicorn || true && sleep 2 && nohup ./venv/bin/python /usr/bin/gunicorn --bind 0.0.0.0:${SERVICE_PORT} --workers 2 --worker-class sync --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 app:app > cdn.log 2>&1 &' || true
            """
            
            echo "Deployment completed successfully!"
          }
        }
      }
      post {
        success {
          script {
            echo "✅ Deployment successful!"
            // Wait a moment for service to start
            sh 'sleep 5'
            
            // Check if gunicorn processes are running
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'ps aux | grep gunicorn | grep -v grep || echo "No gunicorn processes found"'
            """
            
            // Health check with retries
            sh """
              for i in {1..${HEALTH_CHECK_RETRIES}}; do
                echo "Health check attempt \$i/${HEALTH_CHECK_RETRIES}"
                if ssh ${VPS_USER}@${VPS_IP} 'curl -s -f http://localhost:${SERVICE_PORT}/health > /dev/null'; then
                  echo "✅ Health check passed"
                  break
                else
                  echo "❌ Health check failed, attempt \$i"
                  if [ \$i -eq ${HEALTH_CHECK_RETRIES} ]; then
                    echo "❌ All health check attempts failed"
                    exit 1
                  fi
                  sleep 10
                fi
              done
            """
            
            // Check recent logs
            sh """
              ssh ${VPS_USER}@${VPS_IP} 'cd ${APP_DIR} && tail -10 cdn.log || echo "No log file found"'
            """
            
            // Test API endpoints
            sh """
              echo "Testing API endpoints..."
              ssh ${VPS_USER}@${VPS_IP} 'curl -s http://localhost:${SERVICE_PORT}/health | jq .status || echo "Health endpoint test failed"'
            """
          }
        }
        failure {
          script {
            echo "❌ Deployment failed! Attempting rollback..."
            
            // Rollback to previous backup
            sh """
              ssh ${VPS_USER}@${VPS_IP} '
                cd ${APP_DIR}
                LATEST_BACKUP=\$(ls -t ${APP_DIR}-backup-* | head -1)
                if [ -n "\$LATEST_BACKUP" ]; then
                  echo "Rolling back to: \$LATEST_BACKUP"
                  rm -rf ${APP_DIR}-failed-\$(date +%Y%m%d-%H%M%S)
                  mv ${APP_DIR} ${APP_DIR}-failed-\$(date +%Y%m%d-%H%M%S)
                  cp -r \$LATEST_BACKUP ${APP_DIR}
                  cd ${APP_DIR}
                  pkill -f gunicorn || true
                  sleep 2
                  nohup ./venv/bin/python /usr/bin/gunicorn --bind 0.0.0.0:${SERVICE_PORT} --workers 2 --worker-class sync --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 app:app > cdn.log 2>&1 &
                  echo "Rollback completed"
                else
                  echo "No backup found for rollback"
                fi
              '
            """
            
            // Optionally add notification here (email, Slack, etc.)
            echo "Rollback completed. Please check the service manually."
          }
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
