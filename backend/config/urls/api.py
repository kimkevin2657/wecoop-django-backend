from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView, SpectacularJSONAPIView


urlpatterns = [
    path('', include('api.urls')),
    path('health', lambda request: HttpResponse()),
    path('openapi.json', SpectacularJSONAPIView.as_view(), name='schema'),
    path('swagger', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    path('redoc', SpectacularRedocView.as_view(), name='redoc'),
    path('admin', admin.site.urls),
]
