from django.core.management.base import BaseCommand
from bot.services import TelegramBotService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send a test message to Telegram admin'

    def handle(self, *args, **options):
        self.stdout.write('Sending test message to Telegram...')
        
        try:
            bot_service = TelegramBotService()
            
            # Test 1: Simple message
            self.stdout.write('Test 1: Sending simple test message...')
            result1 = bot_service.send_message_to_admin("🧪 Test message from Django management command!")
            
            if result1:
                self.stdout.write(self.style.SUCCESS('✓ Simple message sent successfully!'))
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to send simple message'))
            
            # Test 2: Contact form message
            self.stdout.write('Test 2: Sending contact form test message...')
            result2 = bot_service.send_contact_form_message(
                name="Test User",
                email="test@example.com",
                subject="Test Subject",
                message="This is a test message from the Django management command to verify the Telegram bot is working correctly."
            )
            
            if result2:
                self.stdout.write(self.style.SUCCESS('✓ Contact form message sent successfully!'))
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to send contact form message'))
            
            if result1 and result2:
                self.stdout.write(self.style.SUCCESS('\n✅ All tests passed! Check your Telegram for the messages.'))
            else:
                self.stdout.write(self.style.WARNING('\n⚠️ Some tests failed. Check the logs for details.'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            logger.error(f"Test command error: {str(e)}", exc_info=True)

