from django.urls import path
from .views import SaleCreateView
from . import views

app_name = 'sales'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:sale_id>/", views.detail, name='detail'),
    path("create/", SaleCreateView.as_view(), name='create'),
    path("<int:sale_id>/edit/", views.edit, name='edit'),
    path("<int:sale_id>/delete/", views.delete, name='delete'),
]