from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime
from workspaces.models import WorkspaceUnit, CoWorkingSpace
from .models import Booking, Inquiry
from twilio.rest import Client

def send_whatsapp_notification(to_number, message):
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', 'your_auth_token')
    from_number = getattr(settings, 'TWILIO_FROM_NUMBER', 'whatsapp:+14155238886')

    if not to_number.startswith('whatsapp:'):
        to_number = f"whatsapp:{to_number}"

    # If placeholders are present, print simulation log
    if account_sid.startswith('ACxxx') or auth_token == 'your_auth_token':
        print("\n=== [WHATSAPP SANDBOX SIMULATION] ===")
        print(f"To: {to_number}")
        print(f"From: {from_number}")
        print(f"Body:\n{message}")
        print("======================================\n")
        return False

    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        return True
    except Exception as e:
        print(f"Twilio WhatsApp error: {e}")
        return False


def check_availability_logic(unit, start_date, end_date):
    # Check if there are any conflicting bookings that are APPROVED or PENDING
    conflicts = Booking.objects.filter(
        unit=unit,
        status__in=['PENDING', 'APPROVED']
    ).filter(
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    return not conflicts.exists()

@login_required
def create_booking_view(request):
    if request.method == 'POST':
        unit_id = request.POST.get('unit_id')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        promo_code_str = request.POST.get('promo_code', '').strip().upper()

        if not unit_id or not start_date_str or not end_date_str:
            messages.error(request, "Missing booking dates or workspace selection.")
            return redirect('space_list')

        unit = get_object_or_404(WorkspaceUnit, pk=unit_id)
        
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('space_detail', pk=unit.space.pk)

        # Basic validations
        if start_date < datetime.today().date():
            messages.error(request, "Start date cannot be in the past.")
            return redirect('space_detail', pk=unit.space.pk)

        if end_date < start_date:
            messages.error(request, "End date cannot be before the start date.")
            return redirect('space_detail', pk=unit.space.pk)

        # Availability Check
        if not check_availability_logic(unit, start_date, end_date):
            messages.error(request, "The selected workspace unit is not available for the chosen dates.")
            return redirect('space_detail', pk=unit.space.pk)

        # Promo Code logic
        promo_code = None
        discount_amount = 0.0
        if promo_code_str:
            try:
                from .models import PromoCode
                promo = PromoCode.objects.get(code=promo_code_str, is_active=True)
                promo_code = promo
            except PromoCode.DoesNotExist:
                pass

        # Create Booking
        booking = Booking(
            user=request.user,
            unit=unit,
            start_date=start_date,
            end_date=end_date,
        )
        base_price = booking.calculate_total_price()
        if promo_code:
            from decimal import Decimal
            discount_percent = Decimal(promo_code.discount_percent)
            discount_amount = (base_price * discount_percent) / Decimal(100)
            booking.promo_code = promo_code
            booking.discount_amount = discount_amount
            booking.total_price = base_price - discount_amount
        else:
            booking.total_price = base_price
            
        booking.save()

        # Create In-App Notifications
        from accounts.models import Notification
        Notification.objects.create(
            user=request.user,
            title="Booking Request Submitted",
            message=f"Your booking request for {unit.name} from {start_date} to {end_date} has been submitted (Total: ${booking.total_price})."
        )
        Notification.objects.create(
            user=unit.space.owner,
            title="New Booking Request Received",
            message=f"Client {request.user.username} has requested a booking for {unit.name} from {start_date} to {end_date}."
        )

        # Simulate Email Notification to Space Owner
        owner_email = unit.space.owner.email
        subject = f"New Booking Request: {unit.name} at {unit.space.name}"
        message_body = (
            f"Hello {unit.space.owner.username},\n\n"
            f"You have a new booking request from {request.user.username} for "
            f"{unit.name} ({unit.get_type_display()}) from {start_date} to {end_date}.\n"
            f"Total Price: ${booking.total_price}\n\n"
            f"Please log in to your dashboard to review and approve/reject this request.\n\n"
            f"Best regards,\nCoWork Team"
        )
        try:
            send_mail(
                subject,
                message_body,
                'no-reply@coworkplatform.com',
                [owner_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email failed to send: {e}")

        # Send WhatsApp Notification to Administrator
        whatsapp_msg = (
            f"🔔 *New CoWork Booking Request*\n\n"
            f"📍 *Space:* {unit.space.name}\n"
            f"💼 *Unit:* {unit.name} ({unit.get_type_display()})\n"
            f"👤 *Client:* {request.user.username}\n"
            f"📅 *Dates:* {start_date} to {end_date}\n"
            f"💰 *Total:* ${booking.total_price}\n\n"
            f"Status: Pending Approval."
        )
        to_whatsapp = getattr(settings, 'ADMIN_WHATSAPP_NUMBER', '9380747558')
        send_whatsapp_notification(to_whatsapp, whatsapp_msg)

        # Redirect user immediately to their WhatsApp with populated message
        import urllib.parse
        duration = booking.duration_days()
        promo_info = f"\n🎟️ *Promo Code:* {promo_code.code} ({promo_code.discount_percent}% Off)" if promo_code else ""
        whatsapp_chat_msg = (
            f"🚀 *CoWork Booking Request Submitted!*\n"
            f"-----------------------------------------\n"
            f"📍 *Workspace:* {unit.space.name}\n"
            f"💼 *Unit Type:* {unit.get_type_display()} ({unit.name})\n"
            f"👤 *Client Name:* {request.user.username}\n"
            f"📅 *Duration:* {start_date} to {end_date} ({duration} day{'s' if duration > 1 else ''})\n"
            f"💰 *Daily Rate:* ${unit.price_per_day}/day\n"
            f"🔥 *Total Estimate:* ${booking.total_price}{promo_info}\n"
            f"⚡ *Booking Status:* Pending Owner Approval\n"
            f"-----------------------------------------\n"
            f"Please verify availability and approve my request at your earliest convenience. Thank you!"
        )
        
        encoded_chat_msg = urllib.parse.quote(whatsapp_chat_msg)
        whatsapp_redirect_url = f"https://wa.me/919380747558?text={encoded_chat_msg}"

        messages.success(request, f"Your booking request for '{unit.name}' has been submitted! Redirecting to WhatsApp to notify owner...")
        return redirect(whatsapp_redirect_url)

    return redirect('space_list')

@login_required
def update_booking_status_view(request, pk, status):
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check if the user is the owner of the workspace space
    if booking.unit.space.owner != request.user and not request.user.is_superuser:
        messages.error(request, "You are not authorized to update this booking.")
        return redirect('dashboard_home')

    if status in ['APPROVED', 'REJECTED', 'CANCELLED']:
        booking.status = status
        booking.save()

        # Create In-App Notification
        from accounts.models import Notification
        Notification.objects.create(
            user=booking.user,
            title=f"Booking Request {status.title()}",
            message=f"Your booking request for {booking.unit.name} from {booking.start_date} to {booking.end_date} has been {status.lower()}."
        )

        # Simulate Email Notification to Client
        client_email = booking.user.email
        subject = f"Booking Update: {booking.unit.name} at {booking.unit.space.name}"
        message_body = (
            f"Hello {booking.user.username},\n\n"
            f"Your booking request for {booking.unit.name} from {booking.start_date} to {booking.end_date} "
            f"has been {status.lower()}.\n\n"
            f"Check details in your dashboard.\n\n"
            f"Best regards,\nCoWork Team"
        )
        try:
            send_mail(
                subject,
                message_body,
                'no-reply@coworkplatform.com',
                [client_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email failed: {e}")

        # Send WhatsApp Status Notification to Administrator
        whatsapp_status_msg = (
            f"🔄 *CoWork Booking Status Update*\n\n"
            f"📍 *Space:* {booking.unit.space.name}\n"
            f"💼 *Unit:* {booking.unit.name} ({booking.unit.get_type_display()})\n"
            f"👤 *Client:* {booking.user.username}\n"
            f"📅 *Dates:* {booking.start_date} to {booking.end_date}\n"
            f"💰 *Total:* ${booking.total_price}\n\n"
            f"⚡ *New Status:* {status}"
        )
        to_whatsapp = getattr(settings, 'ADMIN_WHATSAPP_NUMBER', '9380747558')
        send_whatsapp_notification(to_whatsapp, whatsapp_status_msg)

        messages.success(request, f"Booking status updated to {status}.")
    else:
        messages.error(request, "Invalid status action.")

    return redirect('dashboard_home')

@login_required
def cancel_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    # Only the user who booked or admin can cancel
    if booking.user != request.user and not request.user.is_superuser:
        messages.error(request, "You are not authorized to cancel this booking.")
        return redirect('dashboard_home')

    booking.status = 'CANCELLED'
    booking.save()

    # Create In-App Notification for Owner
    from accounts.models import Notification
    Notification.objects.create(
        user=booking.unit.space.owner,
        title="Booking Cancelled by Client",
        message=f"Client {request.user.username} has cancelled their booking for {booking.unit.name} from {booking.start_date} to {booking.end_date}."
    )
    
    messages.success(request, "Your booking has been cancelled.")
    return redirect('dashboard_home')

@login_required
def create_inquiry_view(request, space_id):
    space = get_object_or_404(CoWorkingSpace, pk=space_id)
    if request.method == 'POST':
        message = request.POST.get('message')
        expectations = request.POST.get('expectations', '')
        parent_id = request.POST.get('parent_id')

        parent_inquiry = None
        if parent_id:
            parent_inquiry = get_object_or_404(Inquiry, pk=parent_id)

        inquiry = Inquiry.objects.create(
            sender=request.user,
            space=space,
            message=message,
            expectations=expectations,
            parent=parent_inquiry
        )

        # Create In-App Notification
        from accounts.models import Notification
        if parent_inquiry:
            recipient = parent_inquiry.sender if request.user == space.owner else space.owner
            title = "New Reply on Inquiry"
            msg_text = f"You received a reply from {request.user.username} regarding {space.name}."
        else:
            recipient = space.owner
            title = "New Workspace Inquiry"
            msg_text = f"Client {request.user.username} has sent an inquiry regarding {space.name}."

        Notification.objects.create(
            user=recipient,
            title=title,
            message=msg_text
        )

        messages.success(request, "Your inquiry / team expectations have been sent successfully.")
        return redirect('space_detail', pk=space.pk)

    return redirect('space_detail', pk=space.pk)

def api_booked_dates(request, unit_id):
    unit = get_object_or_404(WorkspaceUnit, pk=unit_id)
    bookings = Booking.objects.filter(
        unit=unit,
        status__in=['PENDING', 'APPROVED']
    )
    booked_ranges = []
    for b in bookings:
        booked_ranges.append({
            'start': b.start_date.strftime('%Y-%m-%d'),
            'end': b.end_date.strftime('%Y-%m-%d')
        })
    return JsonResponse({'booked_dates': booked_ranges})

def api_validate_promo(request):
    code_str = request.GET.get('code', '').strip().upper()
    try:
        from .models import PromoCode
        promo = PromoCode.objects.get(code=code_str, is_active=True)
        return JsonResponse({'valid': True, 'discount_percent': promo.discount_percent})
    except PromoCode.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Invalid or inactive promo code.'})

