from django.contrib import admin
from .models import Faq

# Register the Faq model with the admin site
@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ["question", "project", "order", "is_published"]
    list_filter = ["project", "is_published"]
    search_fields = ["question", "answer"]
