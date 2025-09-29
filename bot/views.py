from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .services import TelegramBotService

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def webhook_update(request):
    """
    Handle incoming webhook updates from Telegram
    """
    try:
        # Parse the JSON data from Telegram
        update_data = json.loads(request.body)
        
        # Log the update for debugging
        logger.info(f"Received webhook update: {update_data}")
        
        # Extract message information
        if 'message' in update_data:
            message = update_data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user_name = message['from'].get('first_name', 'Unknown')
            
            # Handle different commands
            if text.startswith('/start'):
                response_text = f"Hello {user_name}! This is the ikramov.uz website bot. I'm here to notify you about contact form submissions."
            elif text.startswith('/help'):
                response_text = "Available commands:\n/start - Start the bot\n/help - Show this help message\n/status - Check bot status"
            elif text.startswith('/status'):
                response_text = "Bot is running and ready to receive contact form notifications!"
            else:
                response_text = f"Hi {user_name}! I received your message: '{text}'"
            
            # Send response back to user
            bot_service = TelegramBotService()
            bot_service.send_message_to_user(chat_id, response_text)
        
        # Always return 200 OK to Telegram
        return JsonResponse({'status': 'ok'})
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON received in webhook")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error processing webhook update: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)