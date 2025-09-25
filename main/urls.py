from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Utilisateurs.urls')),
    path('menus/', include('Menus.urls')),
    path('plats/', include('Plats.urls')),
    path('commandes/', include('Commandes.urls')),
    path('avis/', include('Avis.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)