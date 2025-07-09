from django.urls import path
from .views import ExpenseTypeDetailCreateView
from . import views

app_name = 'expense_type_details'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:expense_type_detail_id>/", views.detail, name='detail'),
    path("create/", ExpenseTypeDetailCreateView.as_view(), name='create'),
    path("<int:expense_type_detail_id>/edit/", views.edit, name='edit'),
    path("<int:expense_type_detail_id>/delete/", views.delete, name='delete'),
]