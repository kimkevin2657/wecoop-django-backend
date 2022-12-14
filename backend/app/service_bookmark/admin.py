from django.contrib import admin

from app.service_bookmark.models import ServiceBookmark


@admin.register(ServiceBookmark)
class ServiceBookmarkAdmin(admin.ModelAdmin):
    list_display = ["user", "service"]
