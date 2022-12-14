from config.mail_send import send_mail, send_sms
from django.contrib import admin

from .models import Service, ServiceImage, ServiceInfo
from app.alert.models import Alert


class ServiceInfoInline(admin.TabularInline):
    model = ServiceInfo
    extra = 0


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 0


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [ServiceInfoInline, ServiceImageInline]
    list_display = ["title", "user", "score", "menu", "category", "sub_category", "created", "id"]
    search_fields = ["title", "score", "user__nickname", "menu", "category", "sub_category", "code", "id"]
    autocomplete_fields = ["user"]

    def save_form(self, request, form, change):
        input_status = request.POST.get("approve_status")
        instance = super().save_form(request, form, change)
        if change:  # update
            obj = self.get_object(request, request.resolver_match.kwargs["object_id"])
            if input_status:
                user = obj.user

                if input_status == "승인":
                    alert_content = f"({obj.title}) 제출하신 서비스가 승인되었어요. 지금부터 서비스 판매가 가능해요."
                    Alert.objects.create(user=user, type="구글폼 서비스 승인", content=alert_content)
                    send_mail(
                        "admin@wecoop.link",
                        # user.email,
                        "구글폼 서비스 승인",
                        alert_content,
                    )
                    if user.phone:
                        send_sms(user.phone, f"구글폼 서비스 승인 - {alert_content}")

                elif input_status == "미승인":
                    print("11/30(수)에 말씀하신, 모든 미승인 부분은 사유를 입력해야해서 메일/문자 발송 보류 <- 반영")
                    # alert_content = f"({obj.title}) 제출하신 서비스가 미승인되었어요. 자세한 내용은 마이페이지-회원정보에 기재된 이메일에서 확인해 주세요."
                    # Alert.objects.create(user=user, type="구글폼 서비스 미승인", content=alert_content)
                    # send_mail(
                    #     "admin@wecoop.link",
                    #     # user.email,
                    #     "구글폼 서비스 미승인",
                    #     alert_content,
                    # )
                    # if user.phone:
                    #     send_sms(user.phone, f'구글폼 서비스 승인 - {alert_content}')
        elif not change:  # create
            instance.code = Service.generate_code()
        instance.save()

        return instance
