from django.urls import path

from . import api_views

app_name = "documents_api"

urlpatterns = [
    path("", api_views.document_list_api, name="document_list_api"),
]
