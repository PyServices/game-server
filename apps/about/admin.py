from django.contrib import admin
from .models import Credit


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order', 'user')
    list_editable = ('order',)
    search_fields = ('name', 'about')
