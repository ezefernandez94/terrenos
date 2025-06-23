from django.urls import path
from .views import SaleSummaryCreateView
from . import views

app_name = 'sales_summary'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:sale_summary_id>/", views.detail, name='detail'),
    path("create/", SaleSummaryCreateView.as_view(), name='create'),
    path("<int:sale_summary_id>/edit/", views.edit, name='edit'),
    path("<int:sale_summary_id>/delete/", views.delete, name='delete'),
]