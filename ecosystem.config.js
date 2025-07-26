module.exports = {
  apps: [
    {
      name: 'cdn',
      script: 'gunicorn',
      args: '--bind 0.0.0.0:19000 --workers 2 --worker-class sync --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 app:app',
      interpreter: './venv/bin/python',
      cwd: '/opt/tnoradio-cdn-service',
      env: {
        NODE_ENV: 'production',
        BUNNY_STORAGE_API_KEY: process.env.BUNNY_STORAGE_API_KEY,
        BUNNY_API_KEY: process.env.BUNNY_API_KEY,
        BUNNY_VIDEO_LIBRARY_ID: process.env.BUNNY_VIDEO_LIBRARY_ID || '286671',
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
    },
  ],
};