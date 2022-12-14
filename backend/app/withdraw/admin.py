from django.contrib import admin

from .models import Withdraw
from app.alert.models import Alert
from config.mail_send import send_mail, send_sms


@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ["user", "withdraw_number", "final_price", "status", "updated", "id"]
    search_fields = ["user__nickname", "final_price", "withdraw_number", "status"]

    def save_form(self, request, form, change):
        input_status = request.POST.get("status")
        instance = super().save_form(request, form, change)
        if change:  # update
            obj = self.get_object(request, request.resolver_match.kwargs["object_id"])
            user = obj.user

            if input_status and input_status == "정산 완료" and obj.status == "정산 대기":  # input이 있고 변경되었을 때
                # user.possible_withdraw_price -= obj.final_price
                # user.save()
                alert_content = "신청하신 수익금 인출이 완료되었어요."
                Alert.objects.create(user=user, type="수익금 인출 완료", content=alert_content)
                if user.is_email_receive:
                    send_mail(user.email, "수익금 인출 완료", alert_content)
                if user.is_sms_receive and user.phone:
                    send_sms(user.phone, f"수익금 인출 완료 - {alert_content}")
            elif input_status and input_status == "정산 미승인" and obj.status == "정산 대기":
                alert_content = "신청하신 수익금 인출이 미승인되었어요. 자세한 내용은 마이페이지-회원정보에 기재된 이메일에서 확인해 주세요."
                Alert.objects.create(user=user, type="수익금 인출 미승인", content=alert_content)
                if user.is_email_receive:
                    send_mail(user.email, "수익금 인출 미승인", alert_content)
                if user.is_sms_receive and user.phone:
                    send_sms(user.phone, f"수익금 인출 미승인 - {alert_content}")

        instance.save()

        return instance
