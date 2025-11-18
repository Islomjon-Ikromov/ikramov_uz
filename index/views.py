from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseServerError
from bot.services import TelegramBotService
from bot.models import ContactMessage

def home(request):
    """Home page view"""
    context = {
        'title': 'Home - MyPage Bootstrap Template',
        'page_name': 'home'
    }
    
    if request.method == 'POST':
        try:
            # Debug CSRF token
            print(f"CSRF Token in POST: {request.POST.get('csrfmiddlewaretoken')}")
            print(f"CSRF Token in COOKIES: {request.COOKIES.get('csrftoken')}")
            
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            subject = request.POST.get('subject', '').strip()
            message_text = request.POST.get('message', '').strip()
            
            # Validate form data
            if not all([name, email, subject, message_text]):
                messages.error(request, 'All fields are required.')
                return render(request, 'index.html', context)
            
            # Save to database
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )
            
            # Send to Telegram
            bot_service = TelegramBotService()
            telegram_sent = bot_service.send_contact_form_message(
                name, email, subject, message_text
            )
            
            if telegram_sent:
                contact_message.sent_to_telegram = True
                contact_message.save()
                messages.success(request, 'Your message has been sent successfully!')
            else:
                messages.warning(request, 'Message saved but could not send notification.')
                
        except Exception as e:
            messages.error(request, 'An error occurred while sending your message.')
            print(f"Error: {str(e)}")
    
    return render(request, 'index.html', context)


def custom_404_view(request, exception):
    """Custom 404 error page"""
    context = {
        'title': '404 - Page Not Found',
        'page_name': '404'
    }
    return render(request, '404.html', context, status=404)


def custom_500_view(request):
    """Custom 500 error page"""
    context = {
        'title': '500 - Server Error',
        'page_name': '500'
    }
    return render(request, '500.html', context, status=500)


def contact_form_ajax(request):
    """AJAX endpoint for contact form submission"""
    if request.method == 'POST':
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            subject = request.POST.get('subject', '').strip()
            message_text = request.POST.get('message', '').strip()
            
            logger.info(f"Contact form submission received: {name}, {email}, {subject}")
            
            # Validate form data
            if not all([name, email, subject, message_text]):
                logger.warning("Contact form validation failed: missing fields")
                return JsonResponse({
                    'success': False,
                    'message': 'All fields are required.'
                }, status=400)
            
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                logger.warning(f"Invalid email format: {email}")
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter a valid email address.'
                }, status=400)
            
            # Save to database
            try:
                contact_message = ContactMessage.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message_text
                )
                logger.info(f"Contact message saved to database: ID {contact_message.id}")
            except Exception as db_error:
                logger.error(f"Database error: {str(db_error)}")
                # Continue even if database save fails, try to send to Telegram
            
            # Send to Telegram
            telegram_sent = False
            try:
                bot_service = TelegramBotService()
                telegram_sent = bot_service.send_contact_form_message(
                    name, email, subject, message_text
                )
                
                if telegram_sent:
                    logger.info("Message sent to Telegram successfully")
                    if 'contact_message' in locals():
                        contact_message.sent_to_telegram = True
                        contact_message.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'Your message has been sent successfully! I will get back to you soon.'
                    })
                else:
                    logger.warning("Failed to send message to Telegram")
                    return JsonResponse({
                        'success': False,
                        'message': 'Message received but could not send notification. Please try contacting via Telegram directly.'
                    })
            except Exception as telegram_error:
                logger.error(f"Telegram error: {str(telegram_error)}")
                return JsonResponse({
                    'success': False,
                    'message': 'Message received but could not send notification. Please try contacting via Telegram directly.'
                })
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in contact_form_ajax: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while sending your message. Please try again later or contact me directly via Telegram.'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
