from django.contrib import admin

from app.service_payment.models import ServicePayment


@admin.register(ServicePayment)
class ServicePaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "payment_number", "service", "price", "status", "created", "id"]
    search_fields = ["user__email", "payment_number", "service__title", "price"]
    autocomplete_fields = ["user"]
