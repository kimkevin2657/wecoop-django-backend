from django.db.models import Q

from rest_framework import views
from rest_framework.response import Response

from .filters import AlertFilter
from .permissions import AlertPermission
from .serializers import (
    AlertListSerializer,
)
from app.alert.models import Alert


class AlertView(views.APIView):
    """
    알림
    ---
    읽음처리, 삭제(전체삭제 포함)에 사용되는 api입니다.
    """

    queryset = Alert.objects.select_related("user")
    serializer_class = AlertListSerializer
    permission_classes = [AlertPermission]
    filterset_class = AlertFilter

    def post(self, request):
        me = request.user
        data = request.data
        print(data)
        if "all_read_delete" in data:
            Alert.objects.filter(Q(user=me) & Q(is_read=True)).delete()
        elif "all_delete" in data:
            Alert.objects.filter(user=me).delete()
        else:
            Alert.objects.filter(Q(user=me) & Q(id__in=data["id"])).delete()
        return Response({"ok": True, "msg": "알림이 삭제되었습니다."})

    def get(self, request):
        query = request.query_params
        if query.get("isMine"):
            return Response(self.queryset.filter(user=self.request.user).values())
        return Response(Alert.objects.select_related("user").values())

    def patch(self, request):
        # 웹페이지에서 알림목록 중 특정알림 클릭 시, body : {is_read: true}
        # 인 상태로 patch하여 업데이트하는 프로세스입니다.
        Alert.objects.filter(id__in=request.data["ids"]).update(is_read=True)
        return Response({"ok": True, "msg": "알림이 읽음처리 되었습니다."})
