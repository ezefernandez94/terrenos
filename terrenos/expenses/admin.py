from django.contrib import admin
from .models import Expense

# Register the Investment model with the admin site
admin.site.register(Expense)