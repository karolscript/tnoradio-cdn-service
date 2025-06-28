pipeline {
  agent any
  environment {
    VPS_USER = 'root'
    VPS_IP = '82.25.79.43'
    APP_NAME = 'tnoradio-cdn-service'
    APP_DIR = "/home/api/${APP_NAME}"
    VENV_DIR = "${APP_DIR}/venv"
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
        git(
          branch: 'main',
          url: 'https://karolscript@bitbucket.org/tnoradio/tnoradio-cdn-service.git',
          credentialsId: 'bitbucket-app-pass'
        )
      }
    }

    stage('Install dependencies') {
      steps {
        sshagent(credentials: ['ssh-tnonetwork']) {
          sh """
            ssh ${VPS_USER}@${VPS_IP} 'mkdir -p ${APP_DIR}'
            rsync -avz --delete . ${VPS_USER}@${VPS_IP}:${APP_DIR} || { echo 'rsync failed'; exit 1; }
            
            ssh ${VPS_USER}@${VPS_IP} '
              cd ${APP_DIR}
              
              # Crear entorno virtual si no existe
              if [ ! -d "${VENV_DIR}" ]; then
                python3 -m venv ${VENV_DIR}
              fi
              
              # Activar entorno virtual e instalar dependencias
              ${VENV_DIR}/bin/pip install --upgrade pip
              ${VENV_DIR}/bin/pip install -r requirements.txt
              
              # Verificar versiones de Python y pip
              ${VENV_DIR}/bin/python --version
              ${VENV_DIR}/bin/pip --version
            ' || { echo 'ssh command failed'; exit 1; }
          """
        }
      }
    }

    stage('Deploy') {
      steps {
        sshagent(credentials: ['ssh-tnonetwork']) {
          sh """
            ssh ${VPS_USER}@${VPS_IP} '
              cd ${APP_DIR}
              pm2 delete ${APP_NAME}
              # Reiniciar la app si ya está en ejecución
              pm2 start ${VENV_DIR}/bin/gunicorn --name ${APP_NAME} --interpreter /home/api/${APP_NAME}/venv/bin/python -- app:app --bind 0.0.0.0:19000
              
              # Guardar la configuración de PM2 para todas las apps
              pm2 save
              
              # Asegurar que PM2 se inicie automáticamente tras un reinicio
              pm2 startup
            ' || { echo 'ssh command failed'; exit 1; }
          """
        }
      }
    }
  }
}
