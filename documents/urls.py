from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [
    path("", views.document_list, name="document_list"),
    path("<int:document_id>/", views.document_detail, name="document_detail"),
    path("<int:document_id>/file/", views.document_file, name="document_file"),
    path("<int:document_id>/download/", views.document_download, name="document_download"),
]
