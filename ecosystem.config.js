module.exports = {
  apps: [
    {
      name: 'python-app',
      script: 'gunicorn',
      args: '--bind 0.0.0.0:8000 app:app',
      interpreter: 'python3',
      env: {
        NODE_ENV: 'production',
        BUNNY_STORAGE_API_KEY: process.env.BUNNY_STORAGE_API_KEY,
        BUNNY_API_KEY: process.env.BUNNY_API_KEY,
      },
    },
  ],
};