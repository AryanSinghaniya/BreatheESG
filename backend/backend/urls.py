from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_view(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_view, name="health"),
    path("api/", include("ingestion.urls")),
]
