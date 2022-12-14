import json

import requests
from .info_serializers import (
    CeoInfoSerializer,
    UserCareerSerializer,
    UserCertificateSerializer,
    UserEducationSerializer,
)
from app.user.models import (
    CeoInfo,
    Social,
    SocialKindChoices,
    TotalFile,
    User,
    UserCareer,
    UserCertificate,
    UserDeleteReason,
    UserEducation,
)
from app.alert.models import Alert
from app.service.models import Service
from app.service_request.models import ServiceRequest
from app.user.social_adapters import SocialAdapter
from config.mail_send import send_mail, send_sms
from config.response_msg import response
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Q
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_409_CONFLICT,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    UserLoginSerializer,
    UserLogoutSerializer,
    UserProfileSerializer,
    UserSerializer,
    UserSocialLoginSerializer,
)


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
    로그아웃하기위해 사용합니다.
    """

    serializer_class = UserLogoutSerializer
    permission_classes = [IsAuthenticated]


class UserRefreshView(TokenRefreshView):
    """
    유저 토큰리프레시
    ---
    refresh토큰으로 새로운 access토큰과 refresh토큰을 요청합니다.
    """


class UserTotalSocialLoginView(CreateAPIView):
    """
    유저 소셜로그인
    ---
    소셜로그인의 callback으로 전달받은 code와 state값으로 로그인 또는 회원가입을 합니다.
    """

    serializer_class = UserSocialLoginSerializer

    def get_social_user_id(self, code, state, redirect_uri):
        for adapter_class in SocialAdapter.__subclasses__():
            if adapter_class.key == state:
                return adapter_class(code, redirect_uri).get_social_user_id()
        raise ModuleNotFoundError(f"{state.capitalize()}Adapter class")

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)

        state = data["state"]
        user_type = data["user_type"]
        auth_type = data["auth_type"]
        if auth_type == "SIGN_IN":
            social_user_email = self.get_social_user_id(data["code"], state, data["redirect_uri"])
            user = User.objects.filter(email=social_user_email)
            if user.exists():
                user = user.first()
                if not user.is_active:
                    # user.is_active = True
                    # user.save()
                    return Response(
                        {
                            "social_user_id": social_user_email,
                            "message": "유형 선택 후 회원가입을 진행해주세요.",
                        },
                        status=HTTP_403_FORBIDDEN,
                    )
                data = dict()
                refresh = RefreshToken.for_user(user)
                data["user"] = UserSerializer(instance=user).data
                data["access_token"] = str(refresh.access_token)
                data["refresh"] = str(refresh)
                return response(HTTP_200_OK, data, None)
            elif user_type is None:
                return Response(
                    {
                        "social_user_id": social_user_email,
                        "message": "유형 선택 후 회원가입을 진행해주세요.",
                    },
                    status=HTTP_403_FORBIDDEN,
                )
        elif auth_type == "SIGN_UP":
            social_user_email = data["social_user_id"]
            user = User.objects.create(
                email=social_user_email,
                name="",
                nickname=social_user_email.split("@")[0],
                type=user_type,
                password=make_password(None),
            )
            Social.objects.create(user=user, kind=state)
            refresh = RefreshToken.for_user(user)

            data = {
                "user": UserSerializer(instance=user).data,
                "access_token": str(refresh.access_token),
                "refresh": str(refresh),
            }
            return response(HTTP_201_CREATED, data, None)


class UserProfileView(APIView):
    """
    유저 회원정보 관련
    ---
    회원탈퇴, 회원정보 수정을 위해 사용합니다.
    """

    permission_classes = [IsAuthenticated]

    # 회원탈퇴
    @transaction.atomic()
    def post(self, request):
        user = request.user

        if (
            ServiceRequest.objects.filter(Q(client=user) | Q(freelancer=user))
            .filter(Q(client_status="working") | Q(freelancer_status="working"))
            .exists()
        ):
            return Response(
                {"message": f"거래중인 서비스가 있어서 탈퇴가 불가능합니다."},
                status=HTTP_403_FORBIDDEN,
            )

        UserDeleteReason.objects.create(
            user_email=user.email, reason=request.data["reason"], user_nickname=user.nickname
        )

        if user.safe_phone:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ3ZWNvb3AiLCJpYXQiOjE2NjY4NTczNzB9.lVYjWmhKstt2V8k3H4x_4gUmaOhJbGnNTkwOwNKeXp8Q9IpM-1rcSAd6FVyj2J9n68EyVD0gHc4ynmUqntO8kA",
            }
            safe_phone_response = requests.post(
                f"https://050api.sejongtelecom.net:8443/050biz/v1/service/clear/{user.safe_phone}", headers=headers
            )
            safe_phone_res = safe_phone_response.json()
            if safe_phone_res["message"] != "SUCCESS":
                return Response(
                    {"msg": f'sejongtelecom error, {safe_phone_res["message"]}'},
                    status=HTTP_403_FORBIDDEN,
                )
            user.safe_phone = None

        user.is_active = False
        user.name = ""
        user.nickname = "탈퇴한 회원"
        user.email = User.generate_email() + "@temp.com"
        user.phone = None
        user.contactable_phone = None
        user.profile_image = None
        user.resident_number = None
        user.account_number = None
        user.bank_name = None

        user.save()
        return Response(status=HTTP_204_NO_CONTENT)

    @transaction.atomic()
    def patch(self, request):
        data = request.data
        me = request.user
        print(data)

        if "education" in data:
            education_serializer = UserEducationSerializer(data=data["education"])
            user_education = UserEducation.objects.filter(user=me)
            if user_education.exists():
                education_serializer = UserEducationSerializer(instance=user_education.first(), data=data["education"])
            education_serializer.is_valid(raise_exception=True)
            education = education_serializer.save(user=me)
            if education.certificate_status == "미확인":
                send_mail("support@wecoop.link", "이력사항 인증 신청", f"{me.nickname}({me.email})님이 학력 인증을 신청하였습니다.\n\n")

        if "careers" in data:
            careers = data["careers"]
            UserCareer.objects.filter(user=me).delete()
            serializer = UserCareerSerializer(data=careers, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=me)
            if UserCareer.objects.filter(Q(user=me) & Q(certificate_status="미확인")).exists():
                send_mail("support@wecoop.link", "이력사항 인증 신청", f"{me.nickname}({me.email})님이 경력 인증을 신청하였습니다.\n\n")

        if "certificates" in data:
            certificates = data["certificates"]
            UserCertificate.objects.filter(user=me).delete()
            serializer = UserCertificateSerializer(data=certificates, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=me)
            if UserCertificate.objects.filter(Q(user=me) & Q(certificate_status="미확인")).exists():
                send_mail("support@wecoop.link", "이력사항 인증 신청", f"{me.nickname}({me.email})님이 자격증 인증을 신청하였습니다.\n\n")

        if "ceo_info" in data:
            serializer = CeoInfoSerializer(data=data["ceo_info"])
            ceo_info = CeoInfo.objects.filter(user=me)
            if ceo_info.exists():
                serializer = CeoInfoSerializer(instance=ceo_info.first(), data=data["ceo_info"])
            serializer.is_valid(raise_exception=True)
            info = serializer.save(user=me)
            if info.certificate_status == "미확인":
                send_mail("support@wecoop.link", "사업자 인증 신청", f"{me.nickname}({me.email})님이 사업자 인증을 신청하였습니다.\n\n")

        user_serializer = UserSerializer(instance=me, context={"request": request}, data=data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        user_info_serializer = UserProfileSerializer(instance=me, context={"request": request})
        data = dict()

        refresh = RefreshToken.for_user(me)

        data["user"] = user_info_serializer.data
        data["access_token"] = str(refresh.access_token)
        data["refresh"] = str(refresh)

        return response(HTTP_200_OK, data, None)


class UserInfoView(RetrieveAPIView):
    """
    특정유저의 마이페이지 조회
    ---
    특정유저의 마이페이지 정보 조회를 위해 사용합니다.
    """

    @transaction.atomic()
    def get(self, request):
        query = request.query_params
        try:
            user = User.objects.get(id=query.get("user_id"))
            user_serializer = UserProfileSerializer(instance=user, context={"request": request})
            data = dict()

            refresh = RefreshToken.for_user(user)
            data["user"] = user_serializer.data
            data["access_token"] = str(refresh.access_token)
            data["refresh"] = str(refresh)

            return response(HTTP_200_OK, data, None)
        except User.DoesNotExist:
            return response(HTTP_403_FORBIDDEN, None, "존재하지 않는 유저입니다.", "USER_NOT_FOUND")


class SmsCertificateView(CreateAPIView):
    """
    다날 SMS 인증
    ---
    SMS인증을 위해 사용합니다.
    """

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        data = self.request.data

        imp_uid = data["imp_uid"]
        get_token_res = requests.post(
            url="https://api.iamport.kr/users/getToken",
            data={
                "imp_key": settings.IAMPORT_API_KEY,
                "imp_secret": settings.IAMPORT_API_SECRET,
            },
        )
        res = get_token_res.json()
        if res["code"] != 0:
            return Response({"msg": res["message"], "code": res["code"]}, status=HTTP_403_FORBIDDEN)

        headers = {"Authorization": res["response"]["access_token"]}
        certificate_res = requests.get(url=f"https://api.iamport.kr/certifications/{imp_uid}", headers=headers)
        iamport_res = certificate_res.json()
        if iamport_res["code"] != 0:
            return Response(
                {"msg": f'iamport error, {iamport_res["message"]}', "code": iamport_res["code"]},
                status=HTTP_403_FORBIDDEN,
            )
        iamport_phone = iamport_res["response"]["phone"]

        me = request.user
        me.phone = iamport_phone
        me.name = iamport_res["response"]["name"]

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ3ZWNvb3AiLCJpYXQiOjE2NjY4NTczNzB9.lVYjWmhKstt2V8k3H4x_4gUmaOhJbGnNTkwOwNKeXp8Q9IpM-1rcSAd6FVyj2J9n68EyVD0gHc4ynmUqntO8kA",
        }
        body = json.dumps(
            {
                "channelId": str(me.nickname),
                "rcvNo1": iamport_phone,
                "endDay": "20991201",
                "vnoName": f"{str(me.nickname)} 안심번호",
                "agingDay": "20991202",
            }
        )

        has_service_certificate = Service.objects.exclude(is_deleted=True).filter(Q(user=me) & Q(approve_status="승인"))

        if has_service_certificate:
            safe_phone_response = requests.post(
                "https://050api.sejongtelecom.net:8443/050biz/v1/service/assign",
                headers=headers,
                data=body,
            )
            safe_phone_res = safe_phone_response.json()
            if safe_phone_res["message"] != "SUCCESS":
                return Response(
                    {"msg": f'sejongtelecom error, {safe_phone_res["message"]}'},
                    status=HTTP_403_FORBIDDEN,
                )
            me.safe_phone = safe_phone_res["data"]
            me.save()

            return Response(
                {
                    "msg": "인증이 완료되었습니다.",
                    "safe_phone": safe_phone_res["data"],
                    "data": iamport_res,
                }
            )
        else:
            me.save()

            return Response(
                {
                    "msg": "인증이 완료되었습니다. 안심번호는 서비스 승인 후에 할당 가능합니다.",
                    "safe_phone": "",
                    "data": iamport_res,
                }
            )


class FileCreateView(CreateAPIView):
    """
    단일 파일업로드
    ---
    s3에 파일 단일업로드를 위해 사용합니다.
    """

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        data = self.request.data
        file = TotalFile.objects.create(file=data["file"])

        return Response(
            {
                "id": file.id,
                "name": file.file.name.split("/")[1],
                "url": file.file.url,
            }
        )


class UserSocialLoginView(APIView):
    """
    유저 소셜로그인(개발용)
    ---
    개발 테스트에만 사용되는 api입니다.
    """

    @transaction.atomic()
    def post(self, request):
        data = request.data
        email = data["email"]
        user_type = data["user_type"]
        social_type = data["social_type"]

        if social_type not in SocialKindChoices:
            return response(HTTP_400_BAD_REQUEST, None, "지원하지 않는 소셜 타입입니다.")

        if User.objects.filter(email=email).exists():
            return response(HTTP_409_CONFLICT, None, "이미 가입된 유저입니다.")
        user, created = User.objects.get_or_create(
            email=email,
            nickname="test",
            type=user_type,
            defaults={
                "password": make_password(None),
            },
        )
        if created:
            Social.objects.create(user=user, kind=social_type)

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ3ZWNvb3AiLCJpYXQiOjE2NjY4NTczNzB9.lVYjWmhKstt2V8k3H4x_4gUmaOhJbGnNTkwOwNKeXp8Q9IpM-1rcSAd6FVyj2J9n68EyVD0gHc4ynmUqntO8kA",
        }
        body = json.dumps(
            {
                "channelId": user.nickname,
                "rcvNo1": "01028627045",
                "endDay": "20991201",
                "vnoName": f"{user.nickname} 안심번호",
                "agingDay": "20991202",
            }
        )
        safe_phone_response = requests.post(
            "https://050api.sejongtelecom.net:8443/050biz/v1/service/assign",
            headers=headers,
            data=body,
        )
        safe_phone_res = safe_phone_response.json()
        if safe_phone_res["message"] != "SUCCESS":
            return Response(
                {"msg": f'sejongtelecom error, {safe_phone_res["message"]}'},
                status=HTTP_403_FORBIDDEN,
            )
        user.safe_phone = safe_phone_res["data"]
        user.save()

        refresh = RefreshToken.for_user(user)
        data = {
            "user": UserSerializer(instance=user).data,
            "safe_phone": safe_phone_res["data"],
            "access_token": str(refresh.access_token),
            "refresh": str(refresh),
        }

        return response(HTTP_201_CREATED, data, None)

    @transaction.atomic()
    def get(self, request):
        query = request.query_params

        if query.get("social_type") not in SocialKindChoices:
            return response(HTTP_400_BAD_REQUEST, None, "지원하지 않는 소셜 타입입니다.")

        try:
            user = User.objects.get(email=query.get("email"))
            if not user.is_active:
                user.is_active = True
                user.save()
            data = dict()
            refresh = RefreshToken.for_user(user)
            data["user"] = UserSerializer(instance=user).data
            data["access_token"] = str(refresh.access_token)
            data["refresh"] = str(refresh)

            return response(HTTP_200_OK, data, None)
        except User.DoesNotExist:
            return response(HTTP_403_FORBIDDEN, None, "존재하지 않는 유저입니다.", "USER_NOT_FOUND")


class AlertSendView(CreateAPIView):
    """
    위쿱 + 문자 + 메일 알림 전송
    ---
    재결제 알림 전송을 위해 사용합니다.
    """

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        data = request.data

        try:
            receiver_id = data["user_id"]
            user = User.objects.get(id=receiver_id)
            msg_type = data["type"]
            msg_content = data["content"]

            if user.is_email_receive:
                send_mail(user.email, msg_type, msg_content)
            if user.is_sms_receive and user.phone:
                send_sms(user.phone, f"{msg_type} - {msg_content}")

            Alert.objects.create(user=user, type=msg_type, content=msg_content)
        except User.DoesNotExist:
            return Response({"msg": "유저가 존재하지 않습니다."}, status=HTTP_403_FORBIDDEN)
        return Response("ok")


class MailSendView(CreateAPIView):
    """
    메일 전송
    ---
    메일전송을 위해 사용합니다.
    """

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        data = request.data
        # send_mail('receiver@gmail.com', '제목', '내용')

        try:
            receiver_id = data["user_id"]
            user = User.objects.get(id=receiver_id)
            if user.is_email_receive:
                send_mail(user.email, data["type"], data["content"])

            Alert.objects.create(user=user, type=data["type"], content=data["content"])
        except User.DoesNotExist:
            return Response({"msg": "유저가 존재하지 않습니다."}, status=HTTP_403_FORBIDDEN)
        return Response("ok")


class NaverSMSTestView(CreateAPIView):
    """
    네이버 sms 테스트 api
    ---
    네이버 sms 테스트를 위해 사용합니다.
    """

    @transaction.atomic()
    def post(self, request):
        res = send_sms("01028627045", f"제목 - 내용")
        print(res.json())
        return response(HTTP_200_OK, None, "문자가 성공적으로 전송되었습니다.")
