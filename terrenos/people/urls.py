from django.urls import path
from .views import PeopleCreateView
from . import views

app_name = 'people'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:people_id>/", views.detail, name='detail'),
    path("create/", PeopleCreateView.as_view(), name='create'),
    path("<int:people_id>/edit/", views.edit, name='edit'),
    path("<int:people_id>/delete/", views.delete, name='delete'),
]