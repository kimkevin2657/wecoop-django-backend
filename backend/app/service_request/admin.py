from django.contrib import admin

from app.service_request.models import ServiceRequest, ServicePlusOption


class ServicePlusOptionInline(admin.TabularInline):
    model = ServicePlusOption
    extra = 0


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    inlines = [ServicePlusOptionInline]
    list_display = ["client", "freelancer", "service", "service_info", "created", "id"]
    search_fields = [
        "client__nickname",
        "freelancer__nickname",
        "service__title",
        "service_info__title",
        "service_info__type",
        "id",
    ]
