from django.contrib import admin
from django.db.models import Avg

from app.service_review.models import ServiceReview


@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "service", "score", "created", "id"]
    search_fields = ["user__nickname", "service__title", "score", "id"]

    def save_form(self, request, form, change):
        instance = super().save_form(request, form, change)
        if change:  # update
            obj = self.get_object(request, request.resolver_match.kwargs["object_id"])

            service = obj.service
            service.score = service.reviews.all().aggregate(avg=Avg("score"))["avg"]
            service.save()

        instance.save()

        return instance
