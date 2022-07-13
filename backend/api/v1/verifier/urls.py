from django.urls import path

from api.v1.verifier.views import EmailVerifierCreateView, EmailVerifierConfirmView, PhoneVerifierCreateView, \
    PhoneVerifierConfirmView

urlpatterns = [
    path('/email_verifier', EmailVerifierCreateView.as_view()),
    path('/email_verifier/confirm', EmailVerifierConfirmView.as_view()),
    path('/phone_verifier', PhoneVerifierCreateView.as_view()),
    path('/phone_verifier/confirm', PhoneVerifierConfirmView.as_view()),
]
