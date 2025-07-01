from django.urls import path
from . import views

urlpatterns = [
    path('', views.transfers, name='transfers'),
    path('history/', views.transfers_history, name='transfers_history'),
    path('transfer_by_phone/', views.transfer_by_phone_view, name='transfer_by_phone'),

]