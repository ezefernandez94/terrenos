from django.urls import path
from .views import LandCreateView
from . import views

app_name = 'lands'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:land_id>/", views.detail, name='detail'),
    path("create/", LandCreateView.as_view(), name='create'),
    path("projects/<int:project_id>/create_multiple/", views.create_multiple, name='create_multiple'),
    path("<int:land_id>/edit/", views.edit, name='edit'),
    path("<int:land_id>/delete/", views.delete, name='delete'),
    path("<int:land_id>/sell/", views.sell, name='sell'),
]