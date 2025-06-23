from django.urls import path
from .views import LandCreateView
from . import views

app_name = 'lands'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:land_id>/", views.detail, name='detail'),
    path("create/", LandCreateView.as_view(), name='create'),
    path("<int:land_id>/edit/", views.edit, name='edit'),
    path("<int:land_id>/delete/", views.delete, name='delete'),
]