from django.contrib import admin
from .models import Profile, Station, Route, BusSchedule, Booking, Payment, Wallet, WalletTransaction, Notification, ChatHistory

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone', 'created_at']
    search_fields = ['user__username', 'full_name']

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'is_active']
    list_filter = ['city', 'is_active']

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['departure', 'destination', 'base_price', 'is_active']

@admin.register(BusSchedule)
class BusScheduleAdmin(admin.ModelAdmin):
    list_display = ['bus_number', 'route', 'departure_time', 'available_seats', 'price', 'status']
    list_filter = ['status', 'departure_time']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['reference', 'user', 'schedule', 'seat_number', 'status', 'total_price', 'booked_at']
    list_filter = ['status']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'user', 'amount', 'method', 'status', 'paid_at']
    list_filter = ['status', 'method']

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance']

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'txn_type', 'description', 'created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'alert_type', 'is_read', 'created_at']
    list_filter = ['alert_type', 'is_read']

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'response', 'created_at']
