from django.urls import path

from archive import views

urlpatterns = [
    path("", views.root_redirect, name="root"),
    path("intern/", views.intern_home, name="intern-home"),
    path("intern/protokolle/<str:protocol_type>/", views.protocol_view, name="protocol-view"),
    path("intern/statuten/<str:document_type>/", views.statute_view, name="statute-view"),
    path("api/files/<int:document_id>/", views.file_view, name="file-view"),
]
