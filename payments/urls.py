from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.payment_view, name='payment_view'),
    path('pay_fine/', views.pay_fine_view, name='pay_fine'),
    path('pay_hcs/', views.pay_hcs_view, name='pay_hcs'),
    path('pay_parking/', views.pay_parking_view, name='pay_parking'),
    path('transfer_to_eco/', views.transfer_to_eco_view, name='transfer_to_eco'),
    path('pay_travel_card/', views.payment_travel_card, name='pay_travel_card'),
]