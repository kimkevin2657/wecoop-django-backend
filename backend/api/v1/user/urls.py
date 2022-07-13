from django.urls import path

from api.v1.user.views import UserRegisterView, UserSocialLoginView, UserLoginView, UserLogoutView, UserMeView, \
    UserPasswordResetCreateView, UserPasswordResetConfirmView, UserRefreshView


urlpatterns = [
    path('/login', UserLoginView.as_view()),
    path('/logout', UserLogoutView.as_view()),
    path('/refresh', UserRefreshView.as_view()),
    path('/social_login', UserSocialLoginView.as_view()),
    path('/register', UserRegisterView.as_view()),
    path('/me', UserMeView.as_view()),
    path('/password_reset', UserPasswordResetCreateView.as_view()),
    path('/password_reset/confirm', UserPasswordResetConfirmView.as_view()),
]
