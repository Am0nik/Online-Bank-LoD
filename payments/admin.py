from django.contrib import admin
from .models import Mulct, HCS, Parking, Travel_Card
# Register your models here.
@admin.register(Mulct)
class MulctAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'fine_number', 'is_paid', 'date')
    search_fields = ('user__username', 'fine_number')
    list_filter = ('is_paid', 'date')


@admin.register(HCS)
class HCSAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'is_paid', 'date')
    search_fields = ('user__username',)
    list_filter = ('is_paid', 'date')

@admin.register(Parking)
class ParkingAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'description', 'date')
    search_fields = ('user__username',)
    list_filter = ('date',)

@admin.register(Travel_Card)
class TravelCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_number', 'balance', 'is_active')
    search_fields = ('user__username', 'card_number')
    list_filter = ('is_active',)