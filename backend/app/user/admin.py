from django.contrib import admin
from django.db.models import Sum

from app.user.models import User, Social, UserEducation, UserCareer, UserCertificate, CeoInfo, UserDeleteReason
from app.service.models import Service
from app.alert.models import Alert

from config.mail_send import send_mail, send_sms


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["email", "nickname", "name"]
    list_display = ["email", "nickname", "has_career_mark", "type", "score", "is_active", "id"]
    list_editable = ["has_career_mark"]
    list_filter = ["is_staff"]
    exclude = ["last_login", "user_permissions"]
    filter_horizontal = ["groups"]

    def score(self, request):
        user_services = Service.objects.select_related("user").exclude(is_deleted=True).filter(user=request)
        if not user_services:
            return 0
        avg_score = user_services.aggregate(Sum("score"))["score__sum"] / user_services.count()
        return avg_score

    score.short_description = "유저 평점"

    def save_form(self, request, form, change):
        input_password = request.POST.get("password")
        instance = super().save_form(request, form, change)

        if not change:  # create
            instance.set_password(input_password)
        else:  # update
            obj = self.get_object(request, request.resolver_match.kwargs["object_id"])
            if input_password and not input_password == obj.password:  # input이 있고 변경되었을 때
                instance.set_password(input_password)
        instance.save()

        return instance


@admin.register(Social)
class SocialAdmin(admin.ModelAdmin):
    list_display = ["user", "kind"]
    search_fields = ["user__nickname", "kind"]


@admin.register(UserEducation)
class UserEducation(admin.ModelAdmin):
    list_display = ["user", "certificate_status"]

    def save_form(self, request, form, change):
        input_status = request.POST.get("certificate_status")
        instance = super().save_form(request, form, change)
        if change:  # update
            obj = self.get_object(request, request.resolver_match.kwargs["object_id"])
            user = obj.user
            alert_content = "학력 인증이 완료되었어요."
            alert_type = "학력 인증 완료"

            if input_status and input_status != "미확인":
                if input_status == "승인":
                    user.has_career_mark = True
                    user.save()
                elif input_status == "미승인":  # input이 있고 변경되었을 때
                    alert_content = "학력 인증이 반려되었어요."
                    alert_type = "학력 인증 반려"

                alert_content += " 자세한 내용은 마이페이지-회원 정보에 기재된 이메일에서 확인해 주세요."
                Alert.objects.create(user=user, type=alert_type, content=alert_content)
                if user.is_email_receive:
                    send_mail(user.email, alert_type, alert_content)
        instance.save()

        return instance


@admin.register(UserCareer)
class UserCareer(admin.ModelAdmin):
    list_display = ["user", "certificate_status"]

    def save_form(self, request, form, change):
        input_status = request.POST.get("certificate_status")
        instance = super().save_form(request, form, change)
        if change:  # update
            obj = self.get_object(request, request.resolver_match.kwargs["object_id"])
            user = obj.user
            alert_content = "이력사항 인증이 완료되었어요."
            alert_type = "이력사항 인증 완료"

            if input_status and input_status != "미확인":
                if input_status == "승인":
                    user.has_career_mark = True
                    user.save()
                elif input_status and input_status == "미승인":  # input이 있고 변경되었을 때
                    alert_content = "이력사항 인증이 반려되었어요."
                    alert_type = "이력사항 인증 반려"

                alert_content += " 자세한 내용은 마이페이지-회원 정보에 기재된 이메일에서 확인해 주세요."
                Alert.objects.create(user=user, type=alert_type, content=alert_content)

                if user.is_email_receive:
                    send_mail(user.email, alert_type, alert_content)
                if user.is_sms_receive and user.phone:
                    send_sms(user.phone, f"{alert_type} - {alert_content}")
        instance.save()

        return instance


@admin.register(UserCertificate)
class UserCertificate(admin.ModelAdmin):
    list_display = ["user", "certificate_status"]

    def save_form(self, request, form, change):
        input_status = request.POST.get("certificate_status")
        instance = super().save_form(request, form, change)
        if change:  # update
            obj = self.get_object(request, request.resolver_match.kwargs["object_id"])
            user = obj.user
            alert_content = "자격증 인증이 완료되었어요."
            alert_type = "자격증 인증 완료"

            if input_status and input_status != "미확인":
                if input_status == "승인":
                    user.has_career_mark = True
                    user.save()
                elif input_status and input_status == "미승인":  # input이 있고 변경되었을 때
                    alert_content = "자격증 인증이 반려되었어요."
                    alert_type = "자격증 인증 반려"

                alert_content += " 자세한 내용은 마이페이지-회원 정보에 기재된 이메일에서 확인해 주세요."
                Alert.objects.create(user=user, type=alert_type, content=alert_content)
                if user.is_email_receive:
                    send_mail(user.email, alert_type, alert_content)
                if user.is_sms_receive and user.phone:
                    send_sms(user.phone, f"{alert_type} - {alert_content}")
        instance.save()

        return instance


@admin.register(CeoInfo)
class CeoInfo(admin.ModelAdmin):
    list_display = ["user", "certificate_status"]

    def save_form(self, request, form, change):
        input_status = request.POST.get("certificate_status")
        instance = super().save_form(request, form, change)
        if change:  # update
            obj = self.get_object(request, request.resolver_match.kwargs["object_id"])
            user = obj.user
            alert_content = "사업자 인증이 완료되었어요."
            alert_type = "사업자 인증 완료"

            if input_status and input_status != "미확인":
                if input_status == "미승인":  # input이 있고 변경되었을 때
                    alert_content = "사업자 인증이 반려되었어요."
                    alert_type = "사업자 인증 반려"

                alert_content += " 자세한 내용은 마이페이지-회원 정보에 기재된 이메일에서 확인해 주세요."
                Alert.objects.create(user=user, type=alert_type, content=alert_content)
                if user.is_email_receive:
                    send_mail(user.email, alert_type, alert_content)
                if user.is_sms_receive and user.phone:
                    send_sms(user.phone, f"{alert_type} - {alert_content}")
        instance.save()

        return instance


@admin.register(UserDeleteReason)
class UserDeleteReason(admin.ModelAdmin):
    pass
