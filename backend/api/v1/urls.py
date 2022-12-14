from django.urls import include, path

urlpatterns = [
    path("/users", include("api.v1.user.urls")),
    path("/services", include("api.v1.service.urls")),
    path("/service_reviews", include("api.v1.service_review.urls")),
    path("/service_payments", include("api.v1.service_payment.urls")),
    path("/service_bookmark", include("api.v1.service_bookmark.urls")),
    path("/portfolio_bookmark", include("api.v1.portfolio_bookmark.urls")),
    path("/portfolios", include("api.v1.portfolio.urls")),
    path("/inquires", include("api.v1.inquiry.urls")),
    path("/alerts", include("api.v1.alert.urls")),
    path("/service_requests", include("api.v1.service_request.urls")),
    path("/chat_rooms", include("api.v1.chat.urls")),
    path("/withdraw", include("api.v1.withdraw.urls")),
]
