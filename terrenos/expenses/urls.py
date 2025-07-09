from django.urls import path
from .views import ExpenseCreateView
from . import views

app_name = 'expenses'

urlpatterns = [
    path("", views.index, name='index'),
    path("<int:expense_id>/", views.detail, name='detail'),
    path("create/", ExpenseCreateView.as_view(), name='create'),
    path("<int:expense_id>/edit/", views.edit, name='edit'),
    path("<int:expense_id>/delete/", views.delete, name='delete'),
    path("<int:expense_id>/serve_file/", views.serve_file, name='serve_file'),
]