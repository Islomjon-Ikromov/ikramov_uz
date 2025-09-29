# Bot Setup Instructions (using pyTelegramBotAPI)

## 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather
3. Send `/newbot` command
4. Follow the instructions to create your bot:
   - Choose a name for your bot
   - Choose a username (must end with 'bot')
5. BotFather will give you a **Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## 2. Configure the Bot Token

The bot token is already configured in your `.env` file:
```
TELEGRAM_BOT_TOKEN=1330587568:AAFk0XEudISYqBs7wFg-ADCNl2K9dEosVxc
```

If you need to change it, edit the `.env` file in your project root.

## 3. Set Up Webhook

The bot is configured to use webhooks instead of polling. You can set up the webhook in two ways:

### Method 1: Via Browser (Easiest)
Simply visit: `https://ikramov.uz/bot/update/`

This will automatically set up the webhook and show you a confirmation page.

### Method 2: Via Command Line
```bash
python manage.py setup_webhook
```

Both methods will set the webhook URL to: `https://ikramov.uz/bot/update/`

## 4. Start Your Bot

1. Search for your bot on Telegram using the username you created
2. Start a chat with your bot
3. Send `/start` command to activate the bot

## 5. Admin Configuration

The admin ID is already configured as `739089730`. If you need to change it:

1. Find your Telegram user ID by messaging `@userinfobot`
2. Update the `.env` file:
   ```
   TELEGRAM_ADMIN_ID=your_user_id_here
   ```

## 6. Test the Contact Form

1. Start your Django server: `python manage.py runserver`
2. Go to `http://127.0.0.1:8000/`
3. Fill out the contact form
4. Submit the form
5. Check your Telegram - you should receive a message!

## 7. Admin Panel

You can view all contact messages in the Django admin:

1. Go to `http://127.0.0.1:8000/admin/`
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. Click on "Contact Messages" to see all submissions

## Webhook Management Commands

- **Set webhook**: `python manage.py setup_webhook`
- **Delete webhook**: `python manage.py delete_webhook`
- **Webhook URL**: `https://ikramov.uz/bot/update/`

## Features

- ✅ Contact form sends messages to Telegram admin using pyTelegramBotAPI
- ✅ Webhook-based bot communication (more efficient than polling)
- ✅ Messages are saved to database
- ✅ Admin panel to view all messages
- ✅ Success/error notifications
- ✅ Form validation
- ✅ Bot command handling (/start, /help, /status)
- ✅ Simple and reliable bot implementation

## Libraries Used

- `pyTelegramBotAPI` - Simple Telegram Bot API wrapper
- `python-decouple` - Environment variable management
- `Django` - Web framework

## Troubleshooting

If messages are not being sent to Telegram:

1. Check that your bot token is correct
2. Make sure you've started the bot with `/start`
3. Verify the admin ID is correct
4. Check Django logs for error messages
5. Ensure your bot has permission to send messages to the admin
6. Make sure the bot token is properly set in the `.env` file

## Security Notes

- Never commit the `.env` file to version control
- Keep your bot token secret
- Use environment variables in production
- Consider rate limiting for the contact form
