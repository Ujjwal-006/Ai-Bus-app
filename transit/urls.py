from django.urls import path, include
from . import views
from accounts.views import (
    login_view, logout_view, register_view,
    account_settings_view, forgot_password_view, reset_password_view
)

app_name = 'transit'

urlpatterns = [
    path('', views.schedules_view, name='schedules'),
    path('login/', login_view, name='login_user'),
    path('logout/', logout_view, name='logout_user'),
    path('register/', register_view, name='register'),
    path('settings/', account_settings_view, name='account_settings'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset-password/', reset_password_view, name='reset_password'),
    path('bookings/', views.my_bookings_view, name='my_bookings'),
    path('seat-selection/', views.seat_selection_view, name='seat_selection'),
    path('payment/<int:booking_id>/', views.payment_view, name='payment'),
    path('cancel/<str:reference>/', views.cancel_booking_view, name='cancel_booking'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('tracking/', views.live_tracking_view, name='live_tracking'),
]
