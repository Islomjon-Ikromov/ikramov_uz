# Production Deployment Guide

## Static Files Configuration

### Current Setup (No WhiteNoise)

The application is configured to serve static files without WhiteNoise:
- Static files are served via Django URLs (always enabled)
- Files are collected in `staticfiles/` directory
- Works with both `DEBUG=True` and `DEBUG=False`
- Simple and reliable setup

## Environment Variables

Make sure these are set in production:

```bash
DEBUG=False
SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_ID=739089730
TELEGRAM_WEBHOOK_URL=https://ikramov.uz/bot/update/
ALLOWED_HOSTS=ikramov.uz,www.ikramov.uz
```

## Deployment Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Create superuser (if needed):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Set up webhook:**
   ```bash
   python manage.py setup_webhook
   # OR visit: https://ikramov.uz/bot/update/
   ```

## Production Server

Use a production WSGI server like Gunicorn:

```bash
gunicorn main.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## Static Files Serving

### Current Setup: Django Only
- Static files served via Django URLs
- Simple setup, works out of the box
- Good for smaller to medium deployments
- No additional dependencies required

### Alternative: Nginx + Django (For High Traffic)
- Configure Nginx to serve static files
- Remove static URLs from Django
- Best performance for high traffic sites

## Troubleshooting

### Static Files Not Loading
1. Check `DEBUG=False` in production
2. Run `python manage.py collectstatic`
3. Verify `STATIC_ROOT` directory exists
4. Check file permissions

### Bot Webhook Issues
1. Visit `https://ikramov.uz/bot/update/` to set webhook
2. Check bot token in environment variables
3. Verify webhook URL is accessible

### Database Issues
1. Run `python manage.py migrate`
2. Check database permissions
3. Verify database connection settings
