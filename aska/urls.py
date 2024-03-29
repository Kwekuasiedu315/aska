from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("", include("web.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("select2/", include("django_select2.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
