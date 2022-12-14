from rest_framework import serializers

from app.user.models import UserEducation, UserCareer, UserCertificate, CeoInfo


class UserEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEducation
        exclude = ["user"]


class UserCareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCareer
        exclude = ["user"]


class UserCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCertificate
        exclude = ["user"]


class CeoInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CeoInfo
        exclude = ["user"]
