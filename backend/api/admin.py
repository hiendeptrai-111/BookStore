from django.contrib import admin
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
# Register your models here.
