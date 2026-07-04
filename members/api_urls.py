from django.urls import path

from . import api_views

app_name = "members_api"

urlpatterns = [
    path("", api_views.member_list_api, name="member_list_api"),
]
