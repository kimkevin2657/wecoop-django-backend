from django.contrib import admin

from app.alert.models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "is_read", "created", "id"]
    search_fields = ["user__nickname", "type", "id"]
