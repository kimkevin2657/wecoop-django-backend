from django.contrib import admin

from app.chat.models import Chat


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ["client", "freelancer", "service", "id"]
    search_fields = ["client__nickname", "freelancer__nickname", "service__title", "id"]
