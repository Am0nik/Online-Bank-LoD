from django.contrib import admin
from .models import Check, Transfer

@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'balance', 'code')
    search_fields = ('account_number', 'user__username')
    list_filter = ('user',)
    ordering = ('-balance',)

    def has_add_permission(self, request):
        return True
    
admin.site.register(Transfer)