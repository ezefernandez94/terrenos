from django.urls import path
from .views import ProjectCreateView
from . import views

app_name = 'projects'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:project_id>/", views.detail, name='detail'),
    path("create/", ProjectCreateView.as_view(), name='create'),
    path("<int:project_id>/edit/", views.edit, name='edit'),
    path("<int:project_id>/delete/", views.delete, name='delete'),
]