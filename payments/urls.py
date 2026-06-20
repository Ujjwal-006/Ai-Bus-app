from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('api/bookings/', views.booking_list_api, name='booking_list_api'),
    path('api/wallet/', views.wallet_api, name='wallet_api'),
    path('api/add-funds/', views.add_funds_api, name='add_funds_api'),
]
