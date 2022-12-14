from django.urls import path

from .views import (
    FileCreateView,
    MailSendView,
    SmsCertificateView,
    UserInfoView,
    UserLogoutView,
    UserProfileView,
    UserRefreshView,
    UserSocialLoginView,
    UserTotalSocialLoginView,
    AlertSendView,
)

urlpatterns = [
    path("/social_login", UserTotalSocialLoginView.as_view()),
    path("/logout", UserLogoutView.as_view()),
    path("/profile", UserProfileView.as_view()),
    path("/info", UserInfoView.as_view()),
    path("/sms_certificate", SmsCertificateView.as_view()),
    path("/file", FileCreateView.as_view()),
    path("/refresh", UserRefreshView.as_view()),
    path("/mail_send", MailSendView.as_view()),
    path("/alert_send", AlertSendView.as_view()),
    # 테스트 api_list
    # path("/naver_sms_test", NaverSMSTestView.as_view()),
    path("/dev_social_login", UserSocialLoginView.as_view()),
]
