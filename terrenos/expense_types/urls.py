from django.urls import path
from .views import ExpenseTypeCreateView
from . import views

app_name = 'expense_types'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:expense_type_id>/", views.detail, name='detail'),
    path("create/", ExpenseTypeCreateView.as_view(), name='create'),
    path("<int:expense_type_id>/edit/", views.edit, name='edit'),
    path("<int:expense_type_id>/delete/", views.delete, name='delete'),
]