from django.urls import path
from . import views

app_name = 'bot'

urlpatterns = [
    path('update/', views.webhook_update, name='webhook_update'),
]
