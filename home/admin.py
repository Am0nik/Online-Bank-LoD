from django.contrib import admin
from .models import Actions

# Register your models here.
@admin.register(Actions)
class ActionsAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'description', 'created_at', 'updated_at', 'active_to')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'icon', 'description', 'active_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )