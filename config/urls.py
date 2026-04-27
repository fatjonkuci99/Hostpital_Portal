from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes
    path('api/auth/', include('apps.accounts.urls')),

    # Template-rendered pages
    path('', include('apps.accounts.template_urls')),
    path('', include('apps.records.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
