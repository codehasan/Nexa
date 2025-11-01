from rest_framework.pagination import PageNumberPagination


class TenObjectPagination(PageNumberPagination):
    page_size = 10
