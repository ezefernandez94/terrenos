from django.urls import path
from .views import PaymentReceiverCreateView
from . import views

app_name = 'payment_receivers'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:payment_receiver_id>/", views.detail, name='detail'),
    path("create/", PaymentReceiverCreateView.as_view(), name='create'),
    path("<int:payment_receiver_id>/edit/", views.edit, name='edit'),
    path("<int:payment_receiver_id>/delete/", views.delete, name='delete'),
]