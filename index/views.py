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
