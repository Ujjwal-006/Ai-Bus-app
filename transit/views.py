from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
import json
from .models import (
    Station, Route, BusSchedule, Booking, Payment,
    Wallet, WalletTransaction, Notification, Profile
)


CITIES = [
    "Mumbai", "Pune", "Delhi", "Bangalore", "Chennai", "Kolkata",
    "Hyderabad", "Ahmedabad", "Jaipur", "Lucknow", "Nagpur",
    "Nashik", "Indore", "Bhopal", "Patna", "Surat", "Visakhapatnam",
    "Kochi", "Coimbatore", "Thiruvananthapuram", "Goa", "Shimla",
    "Manali", "Chandigarh", "Amritsar", "Dehradun", "Rishikesh",
    "Udaipur", "Jodhpur", "Varanasi", "Agra", "Mathura"
]


def seed_data():
    if Station.objects.count() == 0:
        for city in CITIES:
            Station.objects.create(name=f"{city} Central", city=city)
        stations = list(Station.objects.all())
        for i in range(len(stations)):
            for j in range(i + 1, min(i + 4, len(stations))):
                route = Route.objects.create(
                    departure=stations[i],
                    destination=stations[j],
                    distance_km=100 + (j - i) * 50,
                    base_price=150 + (j - i) * 75
                )
                for day_offset in range(7):
                    for hour in [6, 8, 10, 12, 14, 16, 18, 20]:
                        dep_time = timezone.now().replace(hour=hour, minute=0, second=0, microsecond=0) + timezone.timedelta(days=day_offset)
                        arr_time = dep_time + timezone.timedelta(hours=2 + (j - i))
                        price = route.base_price + (hour % 4) * 25
                        BusSchedule.objects.create(
                            route=route,
                            bus_number=f"BUS-{1000 + route.id * 10 + hour}",
                            departure_time=dep_time,
                            arrival_time=arr_time,
                            total_seats=60,
                            available_seats=60 - (hour % 8) * 3,
                            price=price,
                        )


def schedules_view(request):
    seed_data()
    departure = request.GET.get('departure', '')
    destination = request.GET.get('destination', '')
    journey_date = request.GET.get('journey_date', '')
    schedules = BusSchedule.objects.filter(
        status='scheduled',
        departure_time__gte=timezone.now()
    ).select_related('route', 'route__departure', 'route__destination')

    if departure:
        schedules = schedules.filter(route__departure__city__icontains=departure)
    if destination:
        schedules = schedules.filter(route__destination__city__icontains=destination)
    if journey_date:
        schedules = schedules.filter(departure_time__date=journey_date)

    return render(request, 'transit/schedules.html', {
        'schedules': schedules[:20],
        'cities_json': json.dumps(CITIES),
        'departure': departure,
        'destination': destination,
        'journey_date': journey_date,
    })


@login_required
def seat_selection_view(request):
    schedule_id = request.GET.get('schedule_id') or request.POST.get('schedule_id')
    if not schedule_id:
        messages.error(request, 'No schedule selected.')
        return redirect('transit:schedules')

    schedule = get_object_or_404(BusSchedule, id=schedule_id)
    booked_seats = list(Booking.objects.filter(
        schedule=schedule, status='upcoming'
    ).values_list('seat_number', flat=True))

    if request.method == 'POST':
        seat = request.POST.get('selected_seat')
        if seat and seat not in booked_seats:
            booking = Booking.objects.create(
                user=request.user,
                schedule=schedule,
                seat_number=seat,
                total_price=schedule.price,
            )
            schedule.available_seats -= 1
            schedule.save()
            return redirect('transit:payment', booking_id=booking.id)

    return render(request, 'transit/seat_selection.html', {
        'schedule': schedule,
        'dep_station': schedule.route.departure.name,
        'dest_station': schedule.route.destination.name,
        'journey_date': schedule.departure_time.strftime('%d %B %Y'),
        'booked_seats': json.dumps(booked_seats),
    })


@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    tax = float(booking.total_price) * 0.05
    total = float(booking.total_price) + tax

    if request.method == 'POST':
        method = request.POST.get('payment_method', 'card')
        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=total,
            method=method,
            status='completed',
            transaction_id=f"TXN-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            paid_at=timezone.now(),
        )
        if method == 'wallet':
            wallet.deduct(total)
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=total,
                txn_type='debit',
                description=f"Booking {booking.reference}",
                reference=booking.reference,
            )
        booking.status = 'upcoming'
        booking.save()
        Notification.objects.create(
            user=request.user,
            title='Booking Confirmed',
            message=f'Your booking {booking.reference} has been confirmed.',
            alert_type='check_circle',
        )
        messages.success(request, 'Payment successful! Booking confirmed.')
        return redirect('transit:my_bookings')

    return render(request, 'transit/payment.html', {
        'booking': booking,
        'wallet': wallet,
        'tax': f"{tax:.2f}",
        'total': f"{total:.2f}",
    })


@login_required
def my_bookings_view(request):
    upcoming = Booking.objects.filter(
        user=request.user, status='upcoming'
    ).select_related('schedule', 'schedule__route', 'schedule__route__departure', 'schedule__route__destination')

    past = Booking.objects.filter(
        user=request.user, status__in=['completed', 'cancelled']
    ).select_related('schedule', 'schedule__route', 'schedule__route__departure', 'schedule__route__destination')

    now = timezone.now()
    for b in upcoming:
        if b.schedule.departure_time < now:
            b.status = 'completed'
            b.save()

    return render(request, 'transit/my_bookings.html', {
        'upcoming_trips': upcoming,
        'past_trips': past,
        'total_count': upcoming.count() + past.count(),
        'upcoming_count': upcoming.count(),
        'completed_count': past.filter(status='completed').count(),
        'cancelled_count': past.filter(status='cancelled').count(),
    })


@login_required
def cancel_booking_view(request, reference):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, reference=reference, user=request.user)
        if booking.status == 'upcoming':
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.save()
            booking.schedule.available_seats += 1
            booking.schedule.save()
            Notification.objects.create(
                user=request.user,
                title='Booking Cancelled',
                message=f'Your booking {reference} has been cancelled.',
                alert_type='warning',
            )
            messages.success(request, 'Booking cancelled successfully.')
    return redirect('transit:my_bookings')


@login_required
def wallet_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet)[:10]
    return render(request, 'transit/wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
    })


@login_required
def alerts_view(request):
    alerts = Notification.objects.filter(user=request.user)[:20]
    if not alerts.exists():
        Notification.objects.bulk_create([
            Notification(user=request.user, title='System Update', message='All networks are operating normally.', alert_type='check_circle'),
            Notification(user=request.user, title='Route Delay', message='Minor delays on Mumbai-Pune corridor.', alert_type='warning', line_tag='Mumbai-Pune'),
            Notification(user=request.user, title='Schedule Change', message='Evening buses updated for Nashik route.', alert_type='schedule', line_tag='Nashik'),
        ])
        alerts = Notification.objects.filter(user=request.user)[:20]
    return render(request, 'transit/alerts.html', {'alerts': alerts})


def live_tracking_view(request):
    return render(request, 'transit/live_tracking.html')
