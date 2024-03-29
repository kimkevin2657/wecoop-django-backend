import json
from os import getenv

import jwt
import requests
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class SocialAdapter:
    key = None

    def __init__(self, code, origin=None):
        self.code = code
        self.origin = origin

    def get_social_user_id(self):
        raise NotImplementedError("Not Implemented 'get_social_user_id' method")


class KakaoAdapter(SocialAdapter):
    key = "kakao"

    def get_social_user_id(self):
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": f"{self.origin}",
            "code": self.code,
            "client_secret": settings.KAKAO_CLIENT_SECRET,
        }
        response = requests.post(url=url, data=data)
        if not response.ok:
            raise ValidationError({"msg": "KAKAO GET TOKEN API ERROR", "detail": response.text, "ok": False})
        data = response.json()

        url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f'Bearer {data["access_token"]}'}
        response = requests.get(url=url, headers=headers)
        if not response.ok:
            raise ValidationError({"msg": "KAKAO GET ME API ERROR", "detail": response.text, "ok": False})
        user = response.json()
        return user["kakao_account"]["email"]
        # return f'{user["properties"]["nickname"]}@kakao.com'


class NaverAdapter(SocialAdapter):
    key = "naver"

    def get_social_user_id(self):
        url = "https://nid.naver.com/oauth2.0/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "code": self.code,
        }
        response = requests.post(url=url, data=data)
        if not response.ok:
            raise ValidationError({"msg": "NAVER GET ME API ERROR", "detail": response.text, "ok": False})
        data = response.json()

        url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f'Bearer {data["access_token"]}'}
        response = requests.post(url=url, headers=headers)
        if not response.ok:
            raise ValidationError({"msg": "NAVER ME ME API ERROR", "detail": response.text, "ok": False})
        user = response.json()

        return user["response"]["email"]
        # return f'{user["response"]["name"]}@naver.com'


class FacebookAdapter(SocialAdapter):
    key = "facebook"

    def get_social_user_id(self):
        url = "https://graph.facebook.com/v15.0/oauth/access_token"
        # url = "https://graph.facebook.com/v9.0/oauth/access_token"
        params = {
            "client_id": settings.FACEBOOK_CLIENT_ID,
            "client_secret": settings.FACEBOOK_CLIENT_SECRET,
            "redirect_uri": f"{self.origin}/",
            "code": self.code,
        }
        response = requests.get(url=url, params=params)
        if not response.ok:
            raise ValidationError(
                {"msg": "FACEBOOK GET TOKEN API ERROR", "detail": response.json()["error"]["message"]}
            )
        res = response.json()

        url = "https://graph.facebook.com/debug_token"
        params = {
            "input_token": res["access_token"],
            "access_token": f"{settings.FACEBOOK_CLIENT_ID}|{settings.FACEBOOK_CLIENT_SECRET}",
        }
        response = requests.get(url=url, params=params)
        if not response.ok:
            raise ValidationError(
                {
                    "msg": "FACEBOOK ME API ERROR",
                    "detail": response.json()["error"]["message"],
                }
            )
        data = response.json()
        user_id = data["data"]["user_id"]

        user = requests.get(
            url=f'https://graph.facebook.com/v15.0/{user_id}/?access_token={res["access_token"]}'
        ).json()
        return f'{user["name"]}@facebook.com'


class GoogleAdapter(SocialAdapter):
    key = "google"

    def get_social_user_id(self):
        url = "https://oauth2.googleapis.com/token"
        data = {
            "code": self.code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": f"{self.origin}",
            "grant_type": "authorization_code",
        }
        response = requests.post(url=url, data=data)

        if not response.ok:
            raise ValidationError({"msg": "GOOGLE GET TOKEN API ERROR", "detail": response.text})
        data = response.json()
        access_token = data["access_token"]
        res = requests.get(url=f"https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={access_token}")
        user = res.json()

        # decoded = jwt.decode(data["id_token"], "", options={"verify_signature": False})
        return user["email"]
        # return f'{user["name"]}@google.com'


class AppleAdapter(SocialAdapter):
    key = "apple"

    def get_social_user_id(self):
        headers = {"kid": settings.APPLE_KEY_ID}

        payload = {
            "iss": settings.APPLE_TEAM_ID,
            "iat": timezone.datetime.now(),
            "exp": timezone.datetime.now() + timezone.timedelta(hours=1),
            "aud": "https://appleid.apple.com",
            "sub": settings.APPLE_CLIENT_ID,
        }

        client_secret = jwt.encode(
            payload,
            settings.APPLE_CLIENT_SECRET,
            algorithm="ES256",
            headers=headers,
        )

        url = "https://appleid.apple.com/auth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.APPLE_CLIENT_ID,
            "client_secret": client_secret,
            "code": self.code,
        }

        response = requests.post(url=url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})

        if not response.ok:
            raise ValidationError("APPLE GET TOKEN API ERROR")

        data = response.json()
        decoded = jwt.decode(data["id_token"], options={"verify_signature": False})

        return decoded["sub"]
