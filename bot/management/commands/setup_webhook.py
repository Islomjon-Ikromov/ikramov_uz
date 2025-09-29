from django.core.management.base import BaseCommand
from bot.services import TelegramBotService

class Command(BaseCommand):
    help = 'Set up Telegram bot webhook'

    def handle(self, *args, **options):
        bot_service = TelegramBotService()
        
        # Get current webhook info
        webhook_info = bot_service.get_webhook_info()
        if webhook_info:
            self.stdout.write(f"Current webhook URL: {webhook_info.url}")
            self.stdout.write(f"Webhook status: {'Active' if webhook_info.url else 'Not set'}")
        
        # Set webhook
        if bot_service.set_webhook():
            self.stdout.write(
                self.style.SUCCESS('Webhook set successfully!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Failed to set webhook')
            )
