from django.urls import path
from . import views

app_name = 'index'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact_form_ajax, name='contact_form'),
]
