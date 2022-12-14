from django_filters.rest_framework import FilterSet

from app.service_payment.models import ServicePayment


class ServicePaymentFilter(FilterSet):
    class Meta:
        model = ServicePayment
        fields = []
