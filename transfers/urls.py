from django.urls import path
from . import views

urlpatterns = [
    path('', views.transfers, name='transfers'),
    path('transfer_by_phone/', views.transfer_by_phone_view, name='transfer_by_phone'),
    path('transfer_by_account/', views.transfer_by_account_view, name='transfer_by_account'),

]