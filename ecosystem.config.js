module.exports = {
  apps: [
    {
      name: 'cdn',
      script: 'gunicorn',
      args: '--bind 0.0.0.0:19000 app:app',
      interpreter: './venv/bin/python',
      cwd: '/home/api/tnoradio-cdn-service',
      env: {
        NODE_ENV: 'production',
        BUNNY_STORAGE_API_KEY: process.env.BUNNY_STORAGE_API_KEY,
        BUNNY_API_KEY: process.env.BUNNY_API_KEY,
        BUNNY_VIDEO_LIBRARY_ID: process.env.BUNNY_VIDEO_LIBRARY_ID || '286671',
      },
    },
  ],
};