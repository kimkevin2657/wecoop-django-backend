from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response


def response(http_code, data=None, message=None, message_type=None):
    return Response(data={"data": data, "message": message, "type": message_type}, status=http_code)
