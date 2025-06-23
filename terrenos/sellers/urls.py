from django.urls import path
from .views import SellerCreateView
from . import views

app_name = 'sellers'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:seller_id>/", views.detail, name='detail'),
    path("create/", SellerCreateView.as_view(), name='create'),
    path("<int:seller_id>/edit/", views.edit, name='edit'),
    path("<int:seller_id>/delete/", views.delete, name='delete'),
]