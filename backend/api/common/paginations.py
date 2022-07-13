from collections import OrderedDict
from urllib import parse

from django.utils.encoding import force_str
from rest_framework.pagination import CursorPagination as DefaultCursorPagination
from rest_framework.response import Response


class CursorPagination(DefaultCursorPagination):
    page_size = 10
    ordering = ["-created_at"]

    def encode_cursor(self, cursor):
        url = super().encode_cursor(cursor)
        query = parse.urlsplit(force_str(url)).query
        query_dict = dict(parse.parse_qsl(query, keep_blank_values=True))

        return query_dict.get(self.cursor_query_param)

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("next", self.get_next_link()),
                    ("results", data),
                ]
            )
        )
