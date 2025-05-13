from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # ✅ Needed for MEDIA_URL and MEDIA_ROOT
from django.conf.urls.static import static  # ✅ Fixed the incorrect import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # ✅ Add comma for good practice
]

if settings.DEBUG:  # ✅ Best practice: serve media files only in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
