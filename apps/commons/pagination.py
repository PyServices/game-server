"""
Pagination per .cursor/docs/architecture/admin-crud.md

GetAll(..., pageNum=1, limitItem=10)
"""
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_query_param = "pageNum"
    page_size_query_param = "limitItem"
    page_size = 10
    max_page_size = 100
