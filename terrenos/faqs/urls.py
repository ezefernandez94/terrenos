from django.urls import path
from .views import FaqCreateView
from . import views

app_name = 'faqs'

urlpatterns = [
    path("", views.index, name='index'),
    path("create/", FaqCreateView.as_view(), name='create'),
    path("<int:faq_id>/edit/", views.edit, name='edit'),
    path("<int:faq_id>/delete/", views.delete, name='delete'),
]
