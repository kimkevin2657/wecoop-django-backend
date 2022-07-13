from django.contrib.auth.models import AnonymousUser
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView

from app.user.models import User
from api.v1.user.serializers import UserRegisterSerializer, UserSocialLoginSerializer, UserLoginSerializer, \
    UserLogoutSerializer, UserMeSerializer, UserPasswordResetCreateSerializer, \
    UserPasswordResetConfirmSerializer


class UserLoginView(CreateAPIView):
    """
    유저 로그인
    ---
    """
    serializer_class = UserLoginSerializer


class UserLogoutView(CreateAPIView):
    """
    유저 로그아웃
    ---
    모바일앱에서만 사용하며, 유저와 디바이스 토큰의 연결을 끊어주기위해 사용합니다.
    """
    serializer_class = UserLogoutSerializer
    permission_classes = [IsAuthenticated]


class UserRefreshView(TokenRefreshView):
    """
    유저 토큰리프레시
    ---
    refresh토큰으로 새로운 access토큰과 refresh토큰을 요청합니다.
    """


class UserSocialLoginView(CreateAPIView):
    """
    유저 소셜로그인
    ---
    소셜로그인의 callback으로 전달받은 code와 state값으로 로그인 또는 회원가입을 합니다.
    """
    serializer_class = UserSocialLoginSerializer


class UserRegisterView(CreateAPIView):
    """
    유저 회원가입
    ---
    """
    serializer_class = UserRegisterSerializer


class UserMeView(RetrieveAPIView):
    """
    유저 정보
    ---
    """
    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        if not self.request.auth:
            return None
        return self.request.user


class UserPasswordResetCreateView(CreateAPIView):
    """
    유저 비밀번호 재설정 요청
    ---
    이메일을 통해 비밀번호 재설정 가능한 link을 발급받습니다.
    """
    serializer_class = UserPasswordResetCreateSerializer


class UserPasswordResetConfirmView(UpdateAPIView):
    """
    유저 비밀번호 재설정
    ---
    유저 비밀번호 재설정 요청 API를 통해 발급받은 link를 통해 비밀번호를 재설정합니다.
    """
    serializer_class = UserPasswordResetConfirmSerializer

    def get_object(self):
        uid = self.request.data.get('uid')
        uid = force_str(urlsafe_base64_decode(uid))
        try:
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return AnonymousUser()
