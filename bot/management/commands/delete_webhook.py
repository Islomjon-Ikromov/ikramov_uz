from django.core.management.base import BaseCommand
from bot.services import TelegramBotService

class Command(BaseCommand):
    help = 'Delete Telegram bot webhook (use polling instead)'

    def handle(self, *args, **options):
        bot_service = TelegramBotService()
        
        if bot_service.delete_webhook():
            self.stdout.write(
                self.style.SUCCESS('Webhook deleted successfully!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('Failed to delete webhook')
            )
