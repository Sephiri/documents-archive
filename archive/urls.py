from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('intern/', views.intern_index, name='intern_index'),
    path('intern/protokolle/<str:convent_type>/', views.protokolle_view, name='protokolle'),
    path('intern/statuten/<str:slug>/', views.statuten_view, name='statuten'),
    path('api/files/<int:document_id>/', views.file_serve_view, name='file_serve'),
]
