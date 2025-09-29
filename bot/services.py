import telebot
from django.conf import settings
import logging
import requests

logger = logging.getLogger(__name__)

class TelegramBotService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.admin_id = settings.TELEGRAM_ADMIN_ID
        self.webhook_url = settings.TELEGRAM_WEBHOOK_URL
        self.bot = None
    
    def send_message_to_admin(self, message_text):
        """
        Send a message to the admin via Telegram bot
        """
        try:
            if not self.bot_token:
                logger.error("Telegram bot token not configured")
                return False
            
            # Create bot instance if not exists
            if not self.bot:
                self.bot = telebot.TeleBot(self.bot_token)
            
            # Send message to admin
            self.bot.send_message(int(self.admin_id), message_text)
            logger.info(f"Message sent to admin {self.admin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to admin: {str(e)}")
            return False
    
    def send_contact_form_message(self, name, email, subject, message):
        """
        Send contact form data to admin via Telegram
        """
        message_text = f"""
🔔 New Contact Form Submission

👤 Name: {name}
📧 Email: {email}
📝 Subject: {subject}

💬 Message:
{message}

---
Sent from ikramov.uz website
        """
        
        return self.send_message_to_admin(message_text)
    
    def send_message_to_user(self, user_id, message_text):
        """
        Send a message to a specific user via Telegram bot
        """
        try:
            if not self.bot_token:
                logger.error("Telegram bot token not configured")
                return False
            
            # Create bot instance if not exists
            if not self.bot:
                self.bot = telebot.TeleBot(self.bot_token)
            
            # Send message to user
            self.bot.send_message(user_id, message_text)
            logger.info(f"Message sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {str(e)}")
            return False
    
    def set_webhook(self):
        """
        Set webhook URL for the bot
        """
        try:
            if not self.webhook_url:
                logger.error("Webhook URL not configured")
                return False
            
            # Create bot instance if not exists
            if not self.bot:
                self.bot = telebot.TeleBot(self.bot_token)
            
            # Set webhook
            self.bot.set_webhook(url=self.webhook_url)
            logger.info(f"Webhook set to: {self.webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting webhook: {str(e)}")
            return False
    
    def delete_webhook(self):
        """
        Delete webhook for the bot (use polling instead)
        """
        try:
            # Create bot instance if not exists
            if not self.bot:
                self.bot = telebot.TeleBot(self.bot_token)
            
            # Delete webhook
            self.bot.remove_webhook()
            logger.info("Webhook deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting webhook: {str(e)}")
            return False
    
    def get_webhook_info(self):
        """
        Get current webhook information
        """
        try:
            # Create bot instance if not exists
            if not self.bot:
                self.bot = telebot.TeleBot(self.bot_token)
            
            # Get webhook info
            webhook_info = self.bot.get_webhook_info()
            return webhook_info
            
        except Exception as e:
            logger.error(f"Error getting webhook info: {str(e)}")
            return None
