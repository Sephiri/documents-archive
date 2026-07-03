from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    path("", views.member_list, name="member_list"),
    path("profile/", views.member_profile, name="member_profile"),
]