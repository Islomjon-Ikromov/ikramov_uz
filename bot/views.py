from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .services import TelegramBotService

logger = logging.getLogger(__name__)

@csrf_exempt
def webhook_update(request):
    """
    Handle incoming webhook updates from Telegram (POST)
    Set up webhook when accessed via GET
    """
    
    if request.method == 'GET':
        """
        GET request - Set up webhook
        """
        try:
            bot_service = TelegramBotService()
            
            # Get current webhook info
            webhook_info = bot_service.get_webhook_info()
            current_url = webhook_info.url if webhook_info else "Not set"
            
            # Set webhook
            if bot_service.set_webhook():
                response_html = f"""
                <html>
                <head><title>Telegram Bot Webhook Setup</title></head>
                <body>
                    <h1>✅ Telegram Bot Webhook Setup Successful!</h1>
                    <p><strong>Webhook URL:</strong> {bot_service.webhook_url}</p>
                    <p><strong>Previous URL:</strong> {current_url}</p>
                    <p><strong>Status:</strong> Active</p>
                    <hr>
                    <p>Your bot is now configured to receive updates via webhook.</p>
                    <p>You can test it by sending a message to your bot on Telegram.</p>
                </body>
                </html>
                """
                return HttpResponse(response_html)
            else:
                response_html = f"""
                <html>
                <head><title>Telegram Bot Webhook Setup Failed</title></head>
                <body>
                    <h1>❌ Telegram Bot Webhook Setup Failed</h1>
                    <p>Please check your bot token and try again.</p>
                    <p><strong>Target URL:</strong> {bot_service.webhook_url}</p>
                </body>
                </html>
                """
                return HttpResponse(response_html, status=500)
                
        except Exception as e:
            logger.error(f"Error setting webhook via GET request: {str(e)}")
            response_html = f"""
            <html>
            <head><title>Telegram Bot Webhook Error</title></head>
            <body>
                <h1>❌ Error Setting Webhook</h1>
                <p><strong>Error:</strong> {str(e)}</p>
                <p>Please check your configuration and try again.</p>
            </body>
            </html>
            """
            return HttpResponse(response_html, status=500)
    
    elif request.method == 'POST':
        """
        POST request - Handle webhook updates from Telegram
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
    
    else:
        # Method not allowed
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)