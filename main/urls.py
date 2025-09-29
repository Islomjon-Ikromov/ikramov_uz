"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from index.views import custom_404_view, custom_500_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('index.urls')),
    path('bot/', include('bot.urls')),
]

# Custom error handlers
handler404 = custom_404_view
handler500 = custom_500_view
# handler403 = "index.views.custom_403_view"

# --- Static & media files ---
# In DEBUG, Django staticfiles app serves STATIC automatically.
# We only add MEDIA here.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production you normally serve static/media via the web server (Nginx).
    # These fallbacks let Django serve them if you really need it.
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
        re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    ]
