from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from transit.models import Booking, Payment, Wallet, WalletTransaction


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_list_api(request):
    bookings = Booking.objects.filter(user=request.user).values(
        'id', 'reference', 'seat_number', 'status', 'total_price', 'booked_at',
        'schedule__route__departure__name', 'schedule__route__destination__name',
        'schedule__departure_time', 'schedule__bus_number'
    )
    return Response(list(bookings))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_api(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet).values(
        'id', 'amount', 'txn_type', 'description', 'created_at'
    )[:20]
    return Response({
        'balance': str(wallet.balance),
        'transactions': list(transactions),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_funds_api(request):
    amount = float(request.POST.get('amount', 0))
    if amount <= 0:
        return Response({'error': 'Invalid amount'}, status=400)
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    wallet.add_funds(amount)
    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        txn_type='credit',
        description='Wallet Recharge',
    )
    return Response({'balance': str(wallet.balance), 'message': 'Funds added successfully'})
