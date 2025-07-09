from django.urls import path
from .views import InvestmentCreateView
from . import views

app_name = 'investments'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:investment_id>/", views.detail, name='detail'),
    path("create/", InvestmentCreateView.as_view(), name='create'),
    path("<int:investment_id>/edit/", views.edit, name='edit'),
    path("<int:investment_id>/delete/", views.delete, name='delete'),
]