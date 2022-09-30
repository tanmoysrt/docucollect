from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from documentCollector import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("studentportal.urls"))
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
