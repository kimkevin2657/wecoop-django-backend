import jwt
import requests
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from app.logger.models import EmailLog
from api.v1.user.examples import login_examples
from app.user.models import User, Social, SocialKindChoices, Device
from app.user.social_adapters import SocialAdapter
from app.user.validators import validate_password
from app.verifier.models import EmailVerifier, PhoneVerifier


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['uid', 'token']


@extend_schema_serializer(examples=login_examples)
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    device = DeviceSerializer(required=False, write_only=True, allow_null=True, help_text='모바일앱에서만 사용합니다.')
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        self.user = authenticate(request=self.context['request'], email=attrs['email'], password=attrs['password'])
        if self.user:
            refresh = self.get_token(self.user)
        else:
            raise ValidationError(['인증정보가 일치하지 않습니다.'])

        data = dict()
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        if attrs.get('device'):
            self.user.connect_device(**attrs['device'])

        return data

    def create(self, validated_data):
        return validated_data


class UserLogoutSerializer(serializers.Serializer):
    uid = serializers.CharField(required=False, help_text='기기의 고유id')

    def create(self, validated_data):
        user = self.context['request'].user
        if validated_data.get('uid'):
            user.disconnect_device(validated_data['uid'])

        return {}


class UserSocialLoginSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)
    state = serializers.CharField(write_only=True)
    redirect_uri = serializers.URLField(write_only=True)

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    is_register = serializers.BooleanField(read_only=True)

    def validate(self, attrs):
        if attrs['state'] not in SocialKindChoices:
            raise ValidationError({'kind': '지원하지 않는 소셜 타입입니다.'})

        attrs['social_user_id'] = self.get_social_user_id(attrs['code'], attrs['state'])

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        social_user_id = validated_data['social_user_id']
        state = validated_data['state']
        user, created = User.objects.get_or_create(email=f'{social_user_id}@{state}.social', defaults={
            'password': make_password(None),
        })

        if created:
            Social.objects.create(user=user, kind=state)

        refresh = RefreshToken.for_user(user)
        return {
            'access': refresh.access_token,
            'refresh': refresh,
            'is_register': user.is_register,
        }

    def get_social_user_id(self, code, state):
        for adapter_class in SocialAdapter.__subclasses__():
            if adapter_class.key == state:
                return adapter_class(code, self.context['request'].META['HTTP_ORIGIN']).get_social_user_id()
        raise ModuleNotFoundError(f'{state.capitalize()}Adapter class')


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True, required=False)
    email_token = serializers.CharField(write_only=True, required=False, help_text='email verifier를 통해 얻은 token값입니다.')
    phone = serializers.CharField(write_only=True, required=False)
    phone_token = serializers.CharField(write_only=True, required=False, help_text='phone verifier를 통해 얻은 token값입니다.')
    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def get_fields(self):
        fields = super().get_fields()

        if 'email' in User.VERIFY_FIELDS:
            fields['email_token'].required = True
        if 'email' in User.VERIFY_FIELDS or 'email' in User.REGISTER_FIELDS:
            fields['email'].required = True
        if 'phone' in User.VERIFY_FIELDS:
            fields['phone_token'].required = True
        if 'phone' in User.VERIFY_FIELDS or 'phone' in User.REGISTER_FIELDS:
            fields['phone'].required = True
        if 'password' in User.REGISTER_FIELDS:
            fields['password'].required = True
            fields['password_confirm'].required = True

        return fields

    def validate(self, attrs):
        email = attrs.get('email')
        email_token = attrs.pop('email_token', None)
        phone = attrs.get('phone')
        phone_token = attrs.pop('phone_token', None)

        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)

        if 'email' in User.VERIFY_FIELDS:
            # 이메일 토큰 검증
            try:
                self.email_verifier = EmailVerifier.objects.get(email=email, token=email_token)
            except EmailVerifier.DoesNotExist:
                raise ValidationError('이메일 인증을 진행해주세요.')
        if 'email' in User.VERIFY_FIELDS or 'email' in User.REGISTER_FIELDS:
            # 이메일 검증
            if User.objects.filter(email=email).exists():
                raise ValidationError({'email': ['이미 가입된 이메일입니다.']})

        if 'phone' in User.VERIFY_FIELDS:
            # 휴대폰 토큰 검증
            try:
                self.phone_verifier = PhoneVerifier.objects.get(phone=phone, token=phone_token)
            except PhoneVerifier.DoesNotExist:
                raise ValidationError('휴대폰 인증을 진행해주세요.')
        if 'phone' in User.VERIFY_FIELDS or 'phone' in User.REGISTER_FIELDS:
            # 휴대폰 검증
            if User.objects.filter(phone=phone).exists():
                raise ValidationError({'phone': ['이미 가입된 휴대폰입니다.']})

        if 'password' in User.REGISTER_FIELDS:
            errors = {}
            # 비밀번호 검증
            if password != password_confirm:
                errors['password'] = ['비밀번호가 일치하지 않습니다.']
                errors['password_confirm'] = ['비밀번호가 일치하지 않습니다.']
            else:
                try:
                    validate_password(password)
                except DjangoValidationError as error:
                    errors['password'] = list(error)
                    errors['password_confirm'] = list(error)

            if errors:
                raise ValidationError(errors)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            **validated_data,
        )
        if 'email' in User.VERIFY_FIELDS:
            self.email_verifier.delete()
        if 'phone' in User.VERIFY_FIELDS:
            self.phone_verifier.delete()

        refresh = RefreshToken.for_user(user)

        return {
            'access': refresh.access_token,
            'refresh': refresh,
        }


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class UserPasswordResetCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        try:
            user = User.objects.get(**validated_data)
            self.send_password_reset_email(user)
        except User.DoesNotExist:
            pass

        return validated_data

    def send_password_reset_email(self, user):
        request = self.context['request']

        subject = '런투런 비밀번호 초기화 인증 메일'
        context = {
            'domain': 'learn2learn2.com',
            'site_name': '런투런',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http',
        }
        body = loader.render_to_string('password_reset_email.html', context)
        EmailLog.objects.create(
            to=user.email,
            title=subject,
            body=body,
        )


class UserPasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs['password']
        password_confirm = attrs['password_confirm']
        token = attrs['token']
        user = self.instance

        if not user.is_authenticated:
            raise ValidationError('존재하지 않는 유저입니다.')

        if not default_token_generator.check_token(user, token):
            raise ValidationError('이미 비밀번호를 변경하셨습니다.')

        errors = dict()
        if password != password_confirm:
            errors['password'] = ['비밀번호가 일치하지 않습니다.']
            errors['password_confirm'] = ['비밀번호가 일치하지 않습니다.']
        else:
            try:
                validate_password(password)
            except DjangoValidationError as error:
                errors['password'] = list(error)
                errors['password_confirm'] = list(error)
        if errors:
            raise ValidationError(errors)

        return attrs

    def update(self, instance, validated_data):
        password = validated_data['password']
        instance.set_password(password)
        instance.save()

        return instance
