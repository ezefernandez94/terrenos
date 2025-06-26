from django.urls import path
from .views import PayerCreateView
from . import views

app_name = 'payers'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:payer_id>/", views.detail, name='detail'),
    path("create/", PayerCreateView.as_view(), name='create'),
    path("<int:payer_id>/edit/", views.edit, name='edit'),
    path("<int:payer_id>/delete/", views.delete, name='delete'),
]