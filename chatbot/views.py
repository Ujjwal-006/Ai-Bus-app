import json
import random
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from transit.models import ChatHistory, Station, BusSchedule, Booking
from django.utils import timezone


AI_RESPONSES = {
    'greeting': [
        "Hello! I'm TRAJET AI, your transit assistant. How can I help you today?",
        "Welcome to TRAJET! I can help you with bookings, schedules, and more.",
        "Hi there! Need help planning your journey?",
    ],
    'booking_help': [
        "To book a ticket, go to Schedules, select your route and date, choose a seat, and complete payment. It's that simple!",
        "You can book tickets from the Schedules page. Select departure, destination, and date to find available buses.",
    ],
    'cancellation': [
        "To cancel a booking, go to My Bookings, find the booking, and click the Cancel button. Refunds are processed to your wallet.",
        "You can cancel upcoming bookings from the My Bookings page. Cancel at least 2 hours before departure for a full refund.",
    ],
    'wallet_help': [
        "Your TRAJET Wallet stores credits for quick payments. You can add funds from the Wallet page.",
        "Use your wallet balance for instant payments. Add funds via card, UPI, or net banking.",
    ],
    'tracking': [
        "Live tracking is available for active buses. Go to the tracking page to see real-time bus locations.",
        "You can track your bus in real-time from the Live Tracking page once your journey begins.",
    ],
    'payment': [
        "We accept Credit/Debit Cards, UPI, Net Banking, and TRAJET Wallet payments.",
        "All payments are secure and encrypted. You can pay using card, UPI, net banking, or wallet.",
    ],
    'schedule': [
        "Check the Schedules page for all available routes. We operate buses across major Indian cities.",
        "Buses run from 6 AM to 10 PM on most routes. Check the schedule for specific timings.",
    ],
    'fallback': [
        "I'm not sure I understand. Could you rephrase that? I can help with bookings, schedules, payments, and tracking.",
        "I'm here to help with transit-related queries. Try asking about bookings, schedules, or payments!",
        "That's outside my expertise. I can assist with ticket booking, cancellations, payments, and live tracking.",
    ],
}


def get_ai_response(message):
    msg = message.lower().strip()

    if any(w in msg for w in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
        return random.choice(AI_RESPONSES['greeting'])
    if any(w in msg for w in ['book', 'ticket', 'reserve', 'seat']):
        return random.choice(AI_RESPONSES['booking_help'])
    if any(w in msg for w in ['cancel', 'refund', 'cancellation']):
        return random.choice(AI_RESPONSES['cancellation'])
    if any(w in msg for w in ['wallet', 'balance', 'credit', 'fund', 'money']):
        return random.choice(AI_RESPONSES['wallet_help'])
    if any(w in msg for w in ['track', 'location', 'live', 'where', 'bus']):
        return random.choice(AI_RESPONSES['tracking'])
    if any(w in msg for w in ['pay', 'card', 'upi', 'netbanking', 'payment']):
        return random.choice(AI_RESPONSES['payment'])
    if any(w in msg for w in ['schedule', 'time', 'departure', 'route', 'city']):
        return random.choice(AI_RESPONSES['schedule'])

    if 'cities' in msg or 'routes' in msg:
        cities = list(Station.objects.values_list('city', flat=True).distinct()[:10])
        return f"We operate in these cities: {', '.join(cities)}. Check the Schedules page for routes between them."

    if 'my booking' in msg or 'my trip' in msg:
        return "You can view all your bookings on the My Bookings page. It shows upcoming and past trips with all details."

    if 'help' in msg:
        return "I can help you with:\n- Finding routes and schedules\n- Booking tickets\n- Managing your wallet\n- Live bus tracking\n- Payment methods\n- Cancellations and refunds\n\nWhat would you like to know?"

    return random.choice(AI_RESPONSES['fallback'])


@csrf_exempt
@require_POST
@login_required
def chat_api(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id', '')

        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        response = get_ai_response(message)

        ChatHistory.objects.create(
            user=request.user,
            message=message,
            response=response,
            conversation_id=conversation_id,
        )

        return JsonResponse({
            'response': response,
            'conversation_id': conversation_id,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
def chat_history_api(request):
    messages = ChatHistory.objects.filter(
        user=request.user
    ).order_by('created_at')[:50].values(
        'message', 'response', 'created_at'
    )
    return JsonResponse({'messages': list(messages)})
