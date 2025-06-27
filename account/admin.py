from django.contrib import admin
from .models import CustomUser
# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'surname', 'phone_number', 'email', 'account_number', 'account_type', 'balance')
    search_fields = ('user__username', 'surname', 'phone_number', 'email', 'account_number')
    list_filter = ('account_type',)
    ordering = ('-balance',)

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    