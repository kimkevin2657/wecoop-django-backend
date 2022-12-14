from app.inquiry.models import Inquiry
from django.contrib import admin
from app.alert.models import Alert
from config.mail_send import send_mail, send_sms


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "type", "status", "created", "id"]
    search_fields = ["user__nickname", "title", "type", "status"]

    def save_form(self, request, form, change):
        input_status = request.POST.get("status")
        instance = super().save_form(request, form, change)

        if change:  # update
            obj = self.get_object(request, request.resolver_match.kwargs["object_id"])
            user = obj.user

            if input_status and input_status == "답변 완료" and obj.status == "답변 대기":  # input이 있고 변경되었을 때
                alert_content = "문의하신 내용에 대해 답변드렸어요. 자세한 내용은 마이페이지-회원 정보에 기재된 이메일에서 확인해 주세요."
                Alert.objects.create(user=user, type="문의사항에 대한 답변 전달", content=alert_content)
                if user.is_email_receive:
                    send_mail(user.email, "문의사항에 대한 답변 전달", alert_content)
                if user.is_sms_receive and user.phone:
                    send_sms(user.phone, f"문의사항에 대한 답변 전달 - {alert_content}")

        instance.save()

        return instance
