from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.core.validators import MinValueValidator
from django.urls import reverse, set_urlconf
from users.models import User
from .models import HotelRoom, HotelBooking, HotelChargeItem, HotelShift, EmployeeSchedule, EmployeeAttendance, EmployeeTask
import datetime
from decimal import Decimal

# Custom decorator for hotel staff access
def hotel_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('hotel_login')
        
        user = request.user
        is_allowed = False
        
        if user.role in ['HOTEL', 'AUBERGE', 'SUB_ADMIN'] and user.is_saas_active:
            is_allowed = True
        elif user.role == 'AGENT' and user.parent_hotel and user.parent_hotel.role in ['HOTEL', 'AUBERGE'] and user.parent_hotel.is_saas_active:
            is_allowed = True
            
        if not is_allowed:
            messages.error(request, "Accès restreint aux professionnels de l'hôtellerie avec abonnement actif.")
            return redirect('hotel_promo')
            
        # Delegate context: Swap request.user with parent if it is a sub-agent
        if user.role == 'AGENT' and user.parent_hotel:
            request.actual_user = user
            request.user = user.parent_hotel

        # Force the hotel urlconf on every hotel view to ensure {% url %} tags
        # in templates resolve correctly regardless of middleware/proxy state
        request.urlconf = 'logertogo.urls_hotel'
        set_urlconf('logertogo.urls_hotel')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def hotel_promo(request):
    """
    Landing page for hotels.logertogo.com showing the hotel management software.
    """
    request.urlconf = 'logertogo.urls_hotel'
    set_urlconf('logertogo.urls_hotel')
    if request.user.is_authenticated and request.user.role in ['HOTEL', 'AUBERGE'] and request.user.is_saas_active:
        return redirect('hotel_dashboard')
    
    # Render purchase or activation banner if logged in but not active
    is_inactive_user = request.user.is_authenticated and (request.user.role in ['HOTEL', 'AUBERGE']) and not request.user.is_saas_active
    return render(request, 'hotel/hotel_promo.html', {'is_inactive_user': is_inactive_user})

def hotel_login(request):
    """
    Log in an hotel owner / manager or their receptionist (sub-agent).
    """
    request.urlconf = 'logertogo.urls_hotel'
    set_urlconf('logertogo.urls_hotel')
    
    if request.user.is_authenticated:
        user = request.user
        is_allowed = False
        if user.role in ['HOTEL', 'AUBERGE', 'SUB_ADMIN'] and user.is_saas_active:
            is_allowed = True
        elif user.role == 'AGENT' and user.parent_hotel and user.parent_hotel.role in ['HOTEL', 'AUBERGE'] and user.parent_hotel.is_saas_active:
            is_allowed = True
        if is_allowed:
            return redirect('hotel_dashboard')
        
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        user = authenticate(request, phone_number=phone, password=password)
        if user is not None:
            if user.role in ['HOTEL', 'AUBERGE', 'SUB_ADMIN']:
                login(request, user)
                messages.success(request, f"Bienvenue, {user.company_name or 'Hôtelier'} !")
                if user.is_saas_active:
                    return redirect('hotel_dashboard')
                return redirect('hotel_promo')
            elif user.role == 'AGENT' and user.parent_hotel and user.parent_hotel.role in ['HOTEL', 'AUBERGE']:
                login(request, user)
                messages.success(request, f"Bienvenue, {user.get_full_name() or 'Réceptionniste'} !")
                if user.parent_hotel.is_saas_active:
                    return redirect('hotel_dashboard')
                return redirect('hotel_promo')
            else:
                messages.error(request, "Ce compte n'est pas un profil Hôtel, Auberge ou Réceptionniste de l'établissement.")
        else:
            messages.error(request, "Identifiants invalides.")
            
    return render(request, 'hotel/login.html')

def hotel_register(request):
    """
    Sign up a new hotel / auberge.
    """
    request.urlconf = 'logertogo.urls_hotel'
    set_urlconf('logertogo.urls_hotel')
    if request.user.is_authenticated and request.user.role in ['HOTEL', 'AUBERGE'] and request.user.is_saas_active:
        return redirect('hotel_dashboard')
        
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        phone = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'HOTEL') # HOTEL or AUBERGE
        city = request.POST.get('city', 'LOME')
        
        if User.objects.filter(phone_number=phone).exists():
            messages.error(request, "Ce numéro de téléphone est déjà enregistré.")
        elif email and User.objects.filter(email=email).exists():
            messages.error(request, "Cette adresse e-mail est déjà enregistrée.")
        else:
            try:
                user = User.objects.create_user(
                    phone_number=phone,
                    email=email or None,
                    password=password,
                    company_name=company_name,
                    role=role,
                    agency_city=city,
                    is_saas_active=False # Activation is done by admin upon subscription!
                )
                login(request, user)
                messages.success(request, "Votre compte Établissement a été créé ! En attente d'activation par l'administrateur.")
                return redirect('hotel_promo')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'inscription : {e}")
                
    return render(request, 'hotel/register.html')

def hotel_logout(request):
    request.urlconf = 'logertogo.urls_hotel'
    set_urlconf('logertogo.urls_hotel')
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('hotel_promo')


def log_employee_action(request, action_type, description):
    """
    Log an action made by the currently logged-in receptionist / employee agent.
    """
    if hasattr(request, 'actual_user'):
        employee = request.actual_user
        parent = request.user
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            
        try:
            from management.models import EmployeeActionLog
            EmployeeActionLog.objects.create(
                hotel=parent,
                employee=employee,
                action_type=action_type,
                description=description,
                ip_address=ip
            )
        except Exception:
            pass


def check_employee_absences(manager, is_hotel=True):
    """
    Check today's employee schedules for a manager (hotel or agency).
    If an employee scheduled to work today has not clocked in and is more than 30 minutes late,
    we create an EmployeeAttendance record marked ABSENT and send a notification e-mail.
    """
    from django.utils import timezone
    import datetime
    from management.models import EmployeeSchedule, EmployeeAttendance
    from users.models import User
    from logertogo.emails import send_employee_absence_notification
    
    today = timezone.now().date()
    now_dt = timezone.now()
    day_of_week = today.isoweekday() # 1-7
    
    if is_hotel:
        staff = User.objects.filter(parent_hotel=manager, role='AGENT')
    else:
        staff = User.objects.filter(parent_agency=manager, role='AGENT')
        
    for employee in staff:
        schedule = EmployeeSchedule.objects.filter(employee=employee, day_of_week=day_of_week).first()
        if schedule:
            sched_start = timezone.make_aware(datetime.datetime.combine(today, schedule.start_time))
            if now_dt > (sched_start + datetime.timedelta(minutes=30)):
                attendance, created = EmployeeAttendance.objects.get_or_create(
                    employee=employee,
                    hotel=manager,
                    date=today,
                    defaults={'status': 'ABSENT'}
                )
                
                if not attendance.clock_in and attendance.status != 'ABSENT':
                    attendance.status = 'ABSENT'
                    attendance.notes = "Alerte Absence automatique (retard > 30 minutes)."
                    attendance.save()
                    
                if not attendance.clock_in and attendance.status == 'ABSENT' and (not attendance.notes or "Email envoyé" not in attendance.notes):
                    try:
                        send_employee_absence_notification(manager, employee, schedule.start_time)
                        attendance.notes = (attendance.notes or "") + " [Email envoyé]"
                        attendance.save()
                        
                        from management.models import EmployeeActionLog
                        EmployeeActionLog.objects.create(
                            hotel=manager,
                            employee=employee,
                            action_type="ABSENCE_DETECTED",
                            description=f"Absence constatée automatiquement : n'a pas pointé à son poste prévu à {schedule.start_time.strftime('%H:%M')}."
                        )
                    except Exception:
                        pass


@login_required
@hotel_required
def hotel_dashboard(request):
    """
    Interactive PMS Dashboard.
    """
    hotel = request.user
    rooms = HotelRoom.objects.filter(hotel=hotel)
    bookings = HotelBooking.objects.filter(room__hotel=hotel)
    
    # Stats calculations
    total_rooms = rooms.count()
    occupied_rooms = rooms.filter(status='OCCUPIED').count()
    cleaning_rooms = rooms.filter(status='CLEANING').count()
    maintenance_rooms = rooms.filter(status='MAINTENANCE').count()
    available_rooms = rooms.filter(status='AVAILABLE').count()
    
    occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0
    
    # Today's check-ins and check-outs
    today = timezone.now().date()
    arrivals = bookings.filter(
        check_in__date=today,
        status='PENDING'
    ).select_related('room')
    
    departures = bookings.filter(
        check_out__date=today,
        status='CHECKED_IN'
    ).select_related('room')
    
    # Active Guests list
    active_guests = bookings.filter(status='CHECKED_IN').select_related('room').order_by('-check_in')[:5]
    
    # Revenue (Daily & Monthly)
    today_start = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
    today_end = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))
    
    # Simple calculation of revenue collected today
    daily_revenue = bookings.filter(
        created_at__range=(today_start, today_end)
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    monthly_revenue = bookings.filter(
        created_at__month=today.month,
        created_at__year=today.year
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    # Staff Attendance & Tasks Context
    my_attendance = None
    my_tasks = None
    live_staff = None
    pending_tasks = None
    action_logs = None
    
    if hasattr(request, 'actual_user'):
        # Logged in as receptionist / employee
        my_attendance = EmployeeAttendance.objects.filter(employee=request.actual_user, date=today).first()
        my_tasks = EmployeeTask.objects.filter(employee=request.actual_user, status='PENDING').order_by('due_date')
    else:
        # Logged in as hotel manager / owner
        # Real-time proactive absence check
        check_employee_absences(hotel, is_hotel=True)
        
        live_staff = EmployeeAttendance.objects.filter(hotel=hotel, date=today).select_related('employee')
        pending_tasks = EmployeeTask.objects.filter(hotel=hotel, status='PENDING').select_related('employee')[:5]
        
        from management.models import EmployeeActionLog
        action_logs = EmployeeActionLog.objects.filter(hotel=hotel).select_related('employee')[:15]

    context = {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'cleaning_rooms': cleaning_rooms,
        'maintenance_rooms': maintenance_rooms,
        'available_rooms': available_rooms,
        'occupancy_rate': occupancy_rate,
        'arrivals': arrivals,
        'departures': departures,
        'active_guests': active_guests,
        'daily_revenue': daily_revenue,
        'monthly_revenue': monthly_revenue,
        'rooms': rooms[:6],
        'my_attendance': my_attendance,
        'my_tasks': my_tasks,
        'live_staff': live_staff,
        'pending_tasks': pending_tasks,
        'action_logs': action_logs,
    }
    return render(request, 'hotel/hotel_dashboard.html', context)

@login_required
@hotel_required
def hotel_rooms(request):
    """
    List hotel rooms and suites.
    """
    rooms = HotelRoom.objects.filter(hotel=request.user).order_by('room_number')
    
    status_filter = request.GET.get('status')
    if status_filter:
        rooms = rooms.filter(status=status_filter)
        
    type_filter = request.GET.get('type')
    if type_filter:
        rooms = rooms.filter(room_type=type_filter)
        
    context = {
        'rooms': rooms,
        'room_types': HotelRoom.TypeEnum.choices,
        'status_choices': HotelRoom.StatusEnum.choices,
    }
    return render(request, 'hotel/hotel_rooms.html', context)

@login_required
@hotel_required
def hotel_room_create(request):
    """
    Add a new room or suite to the hotel.
    """
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les gérants de l'établissement peuvent ajouter des chambres.")
        return redirect('hotel_dashboard')
        
    if request.method == 'POST':
        number = request.POST.get('room_number')
        rtype = request.POST.get('room_type')
        price_night = request.POST.get('price_per_night')
        price_hour = request.POST.get('price_per_hour')
        
        wifi = request.POST.get('wifi') == 'on'
        ac = request.POST.get('air_conditioning') == 'on'
        minibar = request.POST.get('minibar') == 'on'
        tv = request.POST.get('tv') == 'on'
        safe = request.POST.get('safe') == 'on'
        balcony = request.POST.get('balcony') == 'on'
        visible_on_portal = request.POST.get('visible_on_portal') == 'on'
        
        if HotelRoom.objects.filter(hotel=request.user, room_number=number).exists():
            messages.error(request, f"La chambre {number} existe déjà.")
        else:
            try:
                room = HotelRoom.objects.create(
                    hotel=request.user,
                    room_number=number,
                    room_type=rtype,
                    price_per_night=Decimal(price_night),
                    price_per_hour=Decimal(price_hour) if price_hour else None,
                    wifi=wifi,
                    air_conditioning=ac,
                    minibar=minibar,
                    tv=tv,
                    safe=safe,
                    balcony=balcony,
                    visible_on_portal=visible_on_portal
                )
                
                # Gestion des images multiples
                images = request.FILES.getlist('images')
                for i, img in enumerate(images):
                    from management.models import HotelRoomImage
                    HotelRoomImage.objects.create(
                        room=room,
                        image_url=img,
                        is_primary=(i == 0)
                    )
                    
                messages.success(request, f"La chambre {number} a été créée avec succès !")
                return redirect('hotel_rooms')
            except Exception as e:
                messages.error(request, f"Erreur : {e}")
                
    return render(request, 'hotel/hotel_room_form.html', {
        'room_types': HotelRoom.TypeEnum.choices,
        'is_create': True
    })

@login_required
@hotel_required
def hotel_room_edit(request, room_id):
    """
    Edit existing room details.
    """
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les gérants de l'établissement peuvent modifier les chambres.")
        return redirect('hotel_dashboard')
        
    room = get_object_or_404(HotelRoom, id=room_id, hotel=request.user)
    
    if request.method == 'POST':
        room.room_number = request.POST.get('room_number')
        room.room_type = request.POST.get('room_type')
        room.price_per_night = Decimal(request.POST.get('price_per_night'))
        
        price_hour = request.POST.get('price_per_hour')
        room.price_per_hour = Decimal(price_hour) if price_hour else None
        
        room.wifi = request.POST.get('wifi') == 'on'
        room.air_conditioning = request.POST.get('air_conditioning') == 'on'
        room.minibar = request.POST.get('minibar') == 'on'
        room.tv = request.POST.get('tv') == 'on'
        room.safe = request.POST.get('safe') == 'on'
        room.balcony = request.POST.get('balcony') == 'on'
        room.visible_on_portal = request.POST.get('visible_on_portal') == 'on'
        
        try:
            room.save()
            # Gestion de la suppression d'images
            delete_ids = request.POST.getlist('delete_images')
            if delete_ids:
                from management.models import HotelRoomImage
                HotelRoomImage.objects.filter(id__in=delete_ids, room=room).delete()
                # Ensure a primary image remains
                remaining = room.images.all()
                if remaining.exists() and not remaining.filter(is_primary=True).exists():
                    first_img = remaining.first()
                    first_img.is_primary = True
                    first_img.save()
            
            # Gestion des images multiples supplémentaires
            images = request.FILES.getlist('images')
            if images:
                from management.models import HotelRoomImage
                has_primary = room.images.filter(is_primary=True).exists()
                for i, img in enumerate(images):
                    is_primary = not has_primary and (i == 0)
                    HotelRoomImage.objects.create(
                        room=room,
                        image_url=img,
                        is_primary=is_primary
                    )
            
            messages.success(request, f"La chambre {room.room_number} a été modifiée avec succès !")
            return redirect('hotel_rooms')
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
            
    return render(request, 'hotel/hotel_room_form.html', {
        'room': room,
        'room_types': HotelRoom.TypeEnum.choices,
        'is_create': False
    })

@login_required
@hotel_required
def hotel_room_toggle_status(request, room_id):
    """
    Quick toggle operational room status (e.g. Cleaning -> Available).
    """
    room = get_object_or_404(HotelRoom, id=room_id, hotel=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in HotelRoom.StatusEnum.choices]:
            room.status = new_status
            room.save()
            messages.success(request, f"Statut de la chambre {room.room_number} mis à jour : {room.get_status_display()}")
    return redirect('hotel_rooms')

@login_required
@hotel_required
def hotel_bookings(request):
    """
    List hotel reservations and walk-ins.
    """
    bookings = HotelBooking.objects.filter(room__hotel=request.user).select_related('room').order_by('-check_in')
    
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
        
    context = {
        'bookings': bookings,
        'status_choices': HotelBooking.StatusEnum.choices
    }
    return render(request, 'hotel/hotel_bookings.html', context)

@login_required
@hotel_required
def hotel_booking_create(request):
    """
    Create a new booking (Walk-in or Advanced Reservation).
    """
    hotel = request.user
    available_rooms = HotelRoom.objects.filter(hotel=hotel, status='AVAILABLE')
    
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        name = request.POST.get('client_name')
        phone = request.POST.get('client_phone')
        email = request.POST.get('client_email')
        id_card = request.POST.get('client_id_card')
        
        check_in_str = request.POST.get('check_in')
        check_out_str = request.POST.get('check_out')
        
        rate_type = request.POST.get('rate_type', 'NIGHTLY') # NIGHTLY or HOURLY
        hours_qty = request.POST.get('hours_qty', 1)
        
        notes = request.POST.get('notes')
        amount_paid = Decimal(request.POST.get('amount_paid', 0))
        payment_method = request.POST.get('payment_method')
        
        room = get_object_or_404(HotelRoom, id=room_id, hotel=hotel)
        
        try:
            # Parse dates
            check_in = timezone.make_aware(datetime.datetime.strptime(check_in_str, '%Y-%m-%dT%H:%M'))
            check_out = timezone.make_aware(datetime.datetime.strptime(check_out_str, '%Y-%m-%dT%H:%M'))
            
            # --- DATE COHERENCE ---
            if check_out <= check_in:
                messages.error(request, "Erreur : La date de départ doit être postérieure à la date d'arrivée.")
                return redirect('hotel_booking_create')
            
            # --- OVERLAPPING RESERVATIONS (DOUBLE BOOKING) PREVENTION ---
            overlapping_bookings = HotelBooking.objects.filter(
                room=room,
                status__in=['PENDING', 'CHECKED_IN'],
                check_in__lt=check_out,
                check_out__gt=check_in
            )
            if overlapping_bookings.exists():
                messages.error(request, "Erreur : La chambre est déjà occupée ou réservée pour cette période.")
                return redirect('hotel_booking_create')
            
            # Amount calculations
            if rate_type == 'HOURLY' and room.price_per_hour:
                qty = int(hours_qty)
                amount_due = room.price_per_hour * qty
            else:
                nights = (check_out.date() - check_in.date()).days
                if nights <= 0:
                    nights = 1 # Minimum 1 night
                amount_due = room.price_per_night * nights
                
            # Get active shift
            active_shift = HotelShift.objects.filter(hotel=hotel, is_closed=False).first()
            
            booking = HotelBooking.objects.create(
                room=room,
                client_name=name,
                client_phone=phone,
                client_email=email or None,
                client_id_card=id_card or None,
                check_in=check_in,
                check_out=check_out,
                amount_due=amount_due,
                amount_paid=amount_paid,
                payment_method=payment_method,
                notes=notes,
                status='PENDING',
                shift=active_shift
            )
            
            # --- RECORD TRANSACTION ---
            if amount_paid > 0:
                from .models import HotelPayment
                HotelPayment.objects.create(
                    booking=booking,
                    shift=active_shift,
                    amount=amount_paid,
                    payment_method=payment_method or 'ESPECES',
                    payment_type='INITIAL'
                )
            
            messages.success(request, f"Réservation créée et validée avec succès pour {name} !")
            return redirect('hotel_booking_detail', booking_id=booking.id)
        except Exception as e:
            messages.error(request, f"Erreur lors de la création : {e}")
            
    return render(request, 'hotel/hotel_booking_form.html', {
        'rooms': available_rooms,
    })

@login_required
@hotel_required
def hotel_booking_detail(request, booking_id):
    """
    Detailed Guest Folio / Invoice containing pricing, charges billing, and operations.
    """
    booking = get_object_or_404(HotelBooking, id=booking_id, room__hotel=request.user)
    charges = booking.charges.all()
    
    context = {
        'booking': booking,
        'charges': charges,
    }
    return render(request, 'hotel/hotel_booking_detail.html', context)

@login_required
@hotel_required
def hotel_booking_print_invoice(request, booking_id):
    """
    Marque Blanche Print Folio
    """
    booking = get_object_or_404(HotelBooking, id=booking_id, room__hotel=request.user)
    charges = booking.charges.all()
    
    context = {
        'booking': booking,
        'charges': charges,
    }
    return render(request, 'hotel/print_invoice_hotel.html', context)

@login_required
@hotel_required
def hotel_booking_checkin(request, booking_id):
    """
    Perform Check-in: Guest arrived. Marks room as OCCUPIED.
    """
    booking = get_object_or_404(HotelBooking, id=booking_id, room__hotel=request.user)
    if request.method == 'POST':
        booking.status = 'CHECKED_IN'
        booking.save()
        
        # Mark room as occupied
        room = booking.room
        room.status = 'OCCUPIED'
        room.save()
        
        messages.success(request, f"Check-in effectué ! La chambre {room.room_number} est maintenant Occupée.")
        
    return redirect('hotel_booking_detail', booking_id=booking.id)

@login_required
@hotel_required
def hotel_booking_checkout(request, booking_id):
    """
    Perform Check-out: Guest leaving. Marks room as CLEANING.
    """
    booking = get_object_or_404(HotelBooking, id=booking_id, room__hotel=request.user)
    if request.method == 'POST':
        # Get active shift
        active_shift = HotelShift.objects.filter(hotel=request.user, is_closed=False).first()
        
        # Ensure outstanding balance is fully paid (or record what they paid)
        final_payment = Decimal(request.POST.get('final_payment', 0))
        payment_method_final = request.POST.get('payment_method_final', 'ESPECES')
        
        booking.amount_paid += final_payment
        booking.status = 'CHECKED_OUT'
        if active_shift:
            booking.shift = active_shift
        booking.save()
        
        # --- RECORD TRANSACTION ---
        if final_payment > 0:
            from .models import HotelPayment
            HotelPayment.objects.create(
                booking=booking,
                shift=active_shift,
                amount=final_payment,
                payment_method=payment_method_final,
                payment_type='FINAL'
            )
        
        # Mark room as cleaning required
        room = booking.room
        room.status = 'CLEANING'
        room.save()
        
        messages.success(request, f"Check-out effectué ! La chambre {room.room_number} est passée en Ménage.")
        
    return redirect('hotel_booking_detail', booking_id=booking.id)

@login_required
@hotel_required
def hotel_booking_add_charge(request, booking_id):
    """
    Add extra billing charge items (restaurant, mini-bar, laundry) to a Guest Folio.
    """
    booking = get_object_or_404(HotelBooking, id=booking_id, room__hotel=request.user)
    if request.method == 'POST':
        label = request.POST.get('label')
        qty = int(request.POST.get('quantity', 1))
        price = Decimal(request.POST.get('price'))
        
        try:
            charge = HotelChargeItem.objects.create(
                booking=booking,
                label=label,
                quantity=qty,
                price=price
            )
            
            # Get active shift to record payment transaction
            active_shift = HotelShift.objects.filter(hotel=request.user, is_closed=False).first()
            
            # Record the payment transaction for this extra charge
            from .models import HotelPayment
            HotelPayment.objects.create(
                booking=booking,
                shift=active_shift,
                amount=charge.total_price,
                payment_method=booking.payment_method or 'ESPECES',
                payment_type='CHARGE'
            )
            
            messages.success(request, f"Prestation '{label}' ajoutée avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur d'ajout : {e}")
            
    return redirect('hotel_booking_detail', booking_id=booking.id)

@login_required
@hotel_required
def hotel_profile(request):
    """
    Manage hotel profile information.
    """
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les gérants de l'hôtel peuvent modifier le paramétrage de l'établissement.")
        return redirect('hotel_dashboard')
        
    hotel = request.user
    if request.method == 'POST':
        hotel.company_name = request.POST.get('company_name')
        hotel.email = request.POST.get('email') or None
        hotel.agency_address = request.POST.get('agency_address')
        hotel.agency_phone_landline = request.POST.get('phone_landline')
        hotel.agency_phone_mobile = request.POST.get('phone_mobile')
        hotel.agency_website = request.POST.get('website')
        hotel.bio = request.POST.get('description')
        
        # Custom parameters
        hotel.agency_rccm = request.POST.get('rccm')
        hotel.agency_nif = request.POST.get('nif')
        
        # Coordinates and City
        hotel.agency_city = request.POST.get('city')
        hotel.agency_neighborhood = request.POST.get('neighborhood')
        
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        if lat and lng:
            try:
                hotel.agency_latitude = float(lat)
                hotel.agency_longitude = float(lng)
            except ValueError:
                pass
                
        try:
            hotel.save()
            messages.success(request, "Informations de l'établissement mises à jour avec succès !")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
            
    from logersn.constants import CITY_CHOICES, TOGO_NEIGHBORHOODS
    context = {
        'city_choices': CITY_CHOICES,
        'togo_neighborhoods': TOGO_NEIGHBORHOODS,
    }
            
    return render(request, 'hotel/hotel_profile.html', context)


@login_required
@hotel_required
def hotel_planning(request):
    import calendar
    today = timezone.now().date()
    
    # Parse year and month from query params, or use current
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except ValueError:
        year = today.year
        month = today.month
        
    if not (1 <= month <= 12):
        month = today.month
        
    # Get all days of the month
    num_days = calendar.monthrange(year, month)[1]
    days = [datetime.date(year, month, d) for d in range(1, num_days + 1)]
    
    # Calculate previous and next month for navigation
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
        
    prev_month_url = f"?year={prev_year}&month={prev_month}"
    next_month_url = f"?year={next_year}&month={next_month}"
    
    month_name_fr = [
        "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ][month]
    
    hotel = request.user
    rooms = HotelRoom.objects.filter(hotel=hotel).order_by('room_number')
    
    # Get all bookings overlapping with this month
    month_start = timezone.make_aware(datetime.datetime(year, month, 1, 0, 0))
    month_end = timezone.make_aware(datetime.datetime(year, month, num_days, 23, 59, 59))
    
    bookings = HotelBooking.objects.filter(
        room__hotel=hotel,
        check_in__lte=month_end,
        check_out__gte=month_start
    ).exclude(status='CANCELLED').select_related('room')
    
    # Build a room-specific data map for the Gantt rendering
    room_data_list = []
    for room in rooms:
        room_bookings = []
        for b in bookings.filter(room=room):
            # Calculate overlap days in this month
            b_start = b.check_in.date()
            b_end = b.check_out.date()
            
            # Capping to month boundaries for visual math
            c_start = max(b_start, datetime.date(year, month, 1))
            c_end = min(b_end, datetime.date(year, month, num_days))
            
            start_day = c_start.day
            end_day = c_end.day
            span = (c_end - c_start).days + 1
            
            room_bookings.append({
                'booking': b,
                'start_day': start_day,
                'end_day': end_day,
                'span': span,
                'left_offset': start_day - 1, # columns to skip
            })
            
        room_data_list.append({
            'room': room,
            'bookings': room_bookings,
        })
        
    context = {
        'year': year,
        'month': month,
        'month_name': month_name_fr,
        'days': days,
        'num_days': num_days,
        'room_data_list': room_data_list,
        'prev_month_url': prev_month_url,
        'next_month_url': next_month_url,
    }
    return render(request, 'hotel/hotel_planning.html', context)


@login_required
@hotel_required
def hotel_analytics(request):
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les gérants de l'établissement ont accès aux rapports financiers.")
        return redirect('hotel_dashboard')
        
    hotel = request.user
    today = timezone.now().date()
    
    # Default to current month
    year = today.year
    month = today.month
    
    num_days = 30 # default
    import calendar
    try:
        num_days = calendar.monthrange(year, month)[1]
    except Exception:
        pass
        
    month_start = timezone.make_aware(datetime.datetime(year, month, 1, 0, 0))
    month_end = timezone.make_aware(datetime.datetime(year, month, num_days, 23, 59, 59))
    
    rooms = HotelRoom.objects.filter(hotel=hotel)
    total_rooms_qty = rooms.count()
    total_available_room_nights = total_rooms_qty * num_days
    
    bookings_this_month = HotelBooking.objects.filter(
        room__hotel=hotel,
        check_in__lte=month_end,
        check_out__gte=month_start
    ).exclude(status='CANCELLED')
    
    # Calculate Occupied Room Nights
    occupied_room_nights = 0
    total_room_revenue = Decimal('0.00')
    total_extra_revenue = Decimal('0.00')
    
    for b in bookings_this_month:
        b_start = max(b.check_in.date(), month_start.date())
        b_end = min(b.check_out.date(), month_end.date())
        nights = (b_end - b_start).days
        if nights <= 0:
            nights = 1
        occupied_room_nights += nights
        
        # Proportional revenue calculation for room nights
        total_room_revenue += b.amount_due
        total_extra_revenue += b.extra_charges
        
    # Occupancy Rate
    occupancy_rate = round((occupied_room_nights / total_available_room_nights * 100), 1) if total_available_room_nights > 0 else 0
    
    # ADR (Average Daily Rate)
    adr = round(total_room_revenue / occupied_room_nights, 0) if occupied_room_nights > 0 else Decimal('0.00')
    
    # RevPAR (Revenue Per Available Room)
    revpar = round(total_room_revenue / total_available_room_nights, 0) if total_available_room_nights > 0 else Decimal('0.00')
    
    total_revenue_collected = bookings_this_month.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
    
    # Breakdown of extras
    extras_list = HotelChargeItem.objects.filter(booking__room__hotel=hotel, created_at__range=(month_start, month_end))
    
    # Group extras by label category (rough categorization)
    categories = {
        'Restaurant & Bar': Decimal('0.00'),
        'Blanchisserie': Decimal('0.00'),
        'Mini-bar': Decimal('0.00'),
        'Autres services': Decimal('0.00')
    }
    
    for item in extras_list:
        label = item.label.lower()
        tot = item.total_price
        if 'biere' in label or 'beer' in label or 'coca' in label or 'jus' in label or 'bar' in label or 'resto' in label or 'manger' in label or 'plat' in label or 'petit' in label or 'dej' in label or 'diner' in label:
            categories['Restaurant & Bar'] += tot
        elif 'blanchisserie' in label or 'lessive' in label or 'lavage' in label or 'fer' in label or 'repassage' in label:
            categories['Blanchisserie'] += tot
        elif 'minibar' in label or 'mini' in label:
            categories['Mini-bar'] += tot
        else:
            categories['Autres services'] += tot
            
    # Monthly growth tracking (let's get past 6 months stats)
    growth_chart_data = []
    for i in range(5, -1, -1):
        target_month = month - i
        target_year = year
        if target_month <= 0:
            target_month += 12
            target_year -= 1
            
        m_start = timezone.make_aware(datetime.datetime(target_year, target_month, 1, 0, 0))
        m_days = calendar.monthrange(target_year, target_month)[1]
        m_end = timezone.make_aware(datetime.datetime(target_year, target_month, m_days, 23, 59, 59))
        
        m_name = ["", "Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"][target_month]
        
        m_rev = HotelBooking.objects.filter(
            room__hotel=hotel,
            created_at__range=(m_start, m_end)
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        growth_chart_data.append({
            'label': f"{m_name} {target_year}",
            'value': int(m_rev)
        })
        
    context = {
        'occupancy_rate': occupancy_rate,
        'adr': adr,
        'revpar': revpar,
        'total_revenue': total_revenue_collected,
        'room_revenue': total_room_revenue,
        'extra_revenue': total_extra_revenue,
        'categories': categories,
        'growth_chart_data': growth_chart_data,
        'month_name': ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"][month],
        'year': year,
    }
    
    return render(request, 'hotel/hotel_analytics.html', context)


@login_required
@hotel_required
def hotel_shifts(request):
    hotel = request.user
    active_shift = HotelShift.objects.filter(hotel=hotel, is_closed=False).first()
    past_shifts = HotelShift.objects.filter(hotel=hotel, is_closed=True).order_by('-end_time')[:10]
    
    expected_cash = Decimal('0.00')
    shift_cash_payments = []
    if active_shift:
        from .models import HotelPayment
        # Sum all cash payments processed under this active shift
        shift_cash_payments = HotelPayment.objects.filter(
            shift=active_shift,
            payment_method='ESPECES'
        )
        cash_revenue = shift_cash_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        expected_cash = active_shift.initial_cash + cash_revenue
        
    context = {
        'active_shift': active_shift,
        'past_shifts': past_shifts,
        'expected_cash': expected_cash,
        'shift_cash_payments': shift_cash_payments,
    }
    return render(request, 'hotel/hotel_shifts.html', context)


@login_required
@hotel_required
def hotel_shift_open(request):
    if request.method == 'POST':
        hotel = request.user
        if HotelShift.objects.filter(hotel=hotel, is_closed=False).exists():
            messages.error(request, "Un shift est déjà en cours d'exécution.")
            return redirect('hotel_shifts')
            
        initial_cash = request.POST.get('initial_cash', 0)
        try:
            HotelShift.objects.create(
                hotel=hotel,
                receptionist=getattr(request, 'actual_user', request.user),
                initial_cash=Decimal(initial_cash),
                is_closed=False
            )
            messages.success(request, f"Shift ouvert avec {initial_cash} FCFA !")
        except Exception as e:
            messages.error(request, f"Erreur d'ouverture : {e}")
            
    return redirect('hotel_shifts')


@login_required
@hotel_required
def hotel_shift_close(request, shift_id):
    shift = get_object_or_404(HotelShift, id=shift_id, hotel=request.user, is_closed=False)
    if request.method == 'POST':
        actual_cash = request.POST.get('actual_cash')
        notes = request.POST.get('notes')
        
        try:
            shift.actual_cash = Decimal(actual_cash)
            shift.notes = notes
            shift.end_time = timezone.now()
            shift.is_closed = True
            shift.save()
            messages.success(request, f"Shift clôturé avec succès. Audit de caisse complété !")
        except Exception as e:
            messages.error(request, f"Erreur de clôture : {e}")
            
    return redirect('hotel_shifts')


@login_required
@hotel_required
def hotel_sub_agents(request):
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les administrateurs de l'hôtel peuvent gérer les collaborateurs.")
        return redirect('hotel_dashboard')
        
    hotel = request.user
    staff = User.objects.filter(parent_hotel=hotel, role='AGENT')
    staff_count = staff.count()
    
    if request.method == 'POST':
        if staff_count >= 5:
            messages.error(request, "Limite de collaborateurs atteinte. Vous ne pouvez pas ajouter plus de 5 sous-agents.")
            return redirect('hotel_sub_agents')
            
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone_number')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        if first_name and last_name and phone and password:
            try:
                phone_clean = phone.replace(' ', '').replace('-', '')
                if not phone_clean.startswith('+') and len(phone_clean) == 8:
                    phone_clean = '+228' + phone_clean
                elif not phone_clean.startswith('+') and len(phone_clean) == 12 and phone_clean.startswith('228'):
                    phone_clean = '+' + phone_clean
                
                if User.objects.filter(phone_number=phone_clean).exists():
                    messages.error(request, "Un utilisateur existe déjà avec ce numéro de téléphone.")
                else:
                    new_agent = User.objects.create_user(
                        phone_number=phone_clean,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        email=email if email else None,
                        role='AGENT',
                        parent_hotel=hotel,
                        is_saas_active=True
                    )
                    messages.success(request, f"Collaborateur {new_agent.get_full_name()} créé avec succès !")
                    return redirect('hotel_sub_agents')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création : {e}")
        else:
            messages.error(request, "Veuillez renseigner tous les champs obligatoires.")
            
    # Enrich staff with today's attendance and schedules
    today = timezone.now().date()
    thirty_days_ago = today - datetime.timedelta(days=30)
    for member in staff:
        member.today_attendance = EmployeeAttendance.objects.filter(employee=member, date=today).first()
        member.schedules_list = EmployeeSchedule.objects.filter(employee=member).order_by('day_of_week')
        # Format weekly planning display
        sched_map = {s.day_of_week: s for s in member.schedules_list}
        member.weekly_planning = []
        for d in range(1, 8):
            if d in sched_map:
                member.weekly_planning.append({
                    'day': d,
                    'active': True,
                    'start': sched_map[d].start_time.strftime("%H:%M"),
                    'end': sched_map[d].end_time.strftime("%H:%M")
                })
            else:
                member.weekly_planning.append({
                    'day': d,
                    'active': False
                })
                
        # --- BI Statistics for the last 30 days ---
        # 1. Total scheduled days in the last 30 days
        scheduled_days_of_week = list(member.schedules_list.values_list('day_of_week', flat=True))
        total_scheduled = 0
        total_scheduled_hours = 0.0
        if scheduled_days_of_week:
            curr = thirty_days_ago
            while curr <= today:
                if curr.isoweekday() in scheduled_days_of_week:
                    total_scheduled += 1
                    s = sched_map.get(curr.isoweekday())
                    if s:
                        start_dt = datetime.datetime.combine(today, s.start_time)
                        end_dt = datetime.datetime.combine(today, s.end_time)
                        if end_dt < start_dt:
                            end_dt += datetime.timedelta(days=1)
                        total_scheduled_hours += (end_dt - start_dt).total_seconds() / 3600.0
                curr += datetime.timedelta(days=1)
        
        # 2. Actual present and late days clocked in
        attendances_30 = EmployeeAttendance.objects.filter(
            employee=member,
            date__range=(thirty_days_ago, today)
        )
        present_days = attendances_30.exclude(status='ABSENT').exclude(clock_in__isnull=True).count()
        late_days = attendances_30.filter(is_late=True).count()
        late_minutes = attendances_30.aggregate(total=Sum('late_minutes'))['total'] or 0
        total_worked_hours = sum([att.total_work_hours for att in attendances_30])
        member.total_worked_hours_30d = round(total_worked_hours, 1)
        member.total_scheduled_hours_30d = round(total_scheduled_hours, 1)
        
        # Calculate Rates
        if total_scheduled > 0:
            member.presence_rate = min(100, round((present_days / total_scheduled) * 100))
            member.absence_days = max(0, total_scheduled - present_days)
            member.absence_rate = max(0, 100 - member.presence_rate)
        else:
            member.presence_rate = 100 if present_days > 0 else 0
            member.absence_days = 0
            member.absence_rate = max(0, 100 - member.presence_rate)
            
        if total_scheduled_hours > 0:
            member.productivity_rate = min(100, round((total_worked_hours / total_scheduled_hours) * 100))
        else:
            member.productivity_rate = 100 if total_worked_hours > 0 else 0
            
        member.present_days = present_days
        member.total_scheduled_days = total_scheduled
        member.late_days = late_days
        member.late_minutes_total = late_minutes
        
        # Lateness rate
        if present_days > 0:
            member.lateness_rate = round((late_days / present_days) * 100)
        else:
            member.lateness_rate = 0
            
        # 3. Productivity (Tasks completion rate)
        tasks_30 = EmployeeTask.objects.filter(
            employee=member,
            created_at__date__range=(thirty_days_ago, today)
        )
        total_tasks = tasks_30.count()
        completed_tasks = tasks_30.filter(status='COMPLETED').count()
        
        member.total_tasks_count = total_tasks
        member.completed_tasks_count = completed_tasks
        if total_tasks > 0:
            member.productivity_rate = round((completed_tasks / total_tasks) * 100)
        else:
            member.productivity_rate = 100  # Default to 100% if no tasks assigned
                
    # All tasks list
    tasks = EmployeeTask.objects.filter(hotel=hotel).order_by('due_date', '-created_at')
    
    # Attendances list for history
    attendance_history = EmployeeAttendance.objects.filter(hotel=hotel).order_by('-date', '-clock_in')[:100]
    
    # Today presence summary
    today_attendances = EmployeeAttendance.objects.filter(hotel=hotel, date=today)
    present_count = today_attendances.filter(status__in=['PRESENT', 'LATE', 'ON_BREAK']).count()
    late_count = today_attendances.filter(status='LATE').count()
            
    context = {
        'staff': staff,
        'staff_count': staff_count,
        'tasks': tasks,
        'attendance_history': attendance_history,
        'present_count': present_count,
        'late_count': late_count,
    }
    return render(request, 'hotel/hotel_sub_agents.html', context)


@login_required
@hotel_required
def hotel_sub_agent_delete(request, agent_id):
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les administrateurs de l'hôtel peuvent gérer les collaborateurs.")
        return redirect('hotel_dashboard')
        
    hotel = request.user
    agent = get_object_or_404(User, id=agent_id, parent_hotel=hotel, role='AGENT')
    agent.delete()
    messages.success(request, f"Collaborateur supprimé avec succès.")
    return redirect('hotel_sub_agents')


@login_required
@hotel_required
def hotel_clock_action(request):
    """
    Pointage d'arrivée, de départ ou de pause pour le réceptionniste connecté.
    """
    if not hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les collaborateurs de réception peuvent utiliser le pointage.")
        return redirect('hotel_dashboard')
        
    employee = request.actual_user
    hotel = request.user
    today = timezone.now().date()
    now_dt = timezone.now()
    
    # Récupérer ou créer le pointage du jour
    attendance, created = EmployeeAttendance.objects.get_or_create(
        employee=employee,
        hotel=hotel,
        date=today
    )
    
    action = request.POST.get('action')
    lat_val = request.POST.get('latitude')
    lng_val = request.POST.get('longitude')
    lat = None
    lng = None
    if lat_val and lng_val:
        try:
            from decimal import Decimal
            lat = Decimal(lat_val)
            lng = Decimal(lng_val)
        except Exception:
            pass
    
    if action == 'in':
        if attendance.clock_in:
            messages.warning(request, "Vous avez déjà pointé votre arrivée aujourd'hui.")
        else:
            attendance.clock_in = now_dt
            attendance.status = 'PRESENT'
            if lat and lng:
                attendance.latitude_in = lat
                attendance.longitude_in = lng
            
            # Calcul du retard éventuel par rapport au planning
            day_of_week = today.isoweekday()  # 1 = Lundi, 7 = Dimanche
            schedule = EmployeeSchedule.objects.filter(employee=employee, day_of_week=day_of_week).first()
            if schedule:
                # Créer des datetime de comparaison pour aujourd'hui
                sched_start = timezone.make_aware(datetime.datetime.combine(today, schedule.start_time))
                if now_dt > sched_start:
                    diff = now_dt - sched_start
                    late_mins = int(diff.total_seconds() // 60)
                    if late_mins > 5:  # Tolérance de 5 minutes
                        attendance.is_late = True
                        attendance.late_minutes = late_mins
                        attendance.status = 'LATE'
                        messages.warning(request, f"Pointage d'arrivée enregistré avec {late_mins} minutes de retard.")
                        # Notification email au gérant de l'hôtel
                        try:
                            from logertogo.emails import send_employee_late_notification
                            send_employee_late_notification(hotel, employee, late_mins, lat, lng)
                        except Exception as email_err:
                            import logging
                            logging.getLogger('django').error(f"❌ [EMAIL ERROR] Erreur envoi retard : {email_err}")
                    else:
                        messages.success(request, "Pointage d'arrivée enregistré à l'heure.")
                else:
                    messages.success(request, "Pointage d'arrivée enregistré à l'heure.")
            else:
                messages.success(request, "Pointage d'arrivée enregistré (aucun planning défini).")
            attendance.save()
            log_employee_action(request, 'CLOCK_IN', f"Pointage d'arrivée enregistré à {now_dt.strftime('%H:%M:%S')} (GPS: {lat or 'N/D'}, {lng or 'N/D'} | Retard: {attendance.late_minutes} min)")
            
    elif action == 'break_start':
        if not attendance.clock_in:
            messages.error(request, "Vous devez d'abord pointer votre arrivée.")
        elif attendance.clock_out:
            messages.error(request, "Votre service est déjà terminé.")
        elif attendance.break_start:
            messages.warning(request, "Vous êtes déjà en pause.")
        else:
            attendance.break_start = now_dt
            attendance.status = 'ON_BREAK'
            attendance.save()
            messages.info(request, "Début de pause enregistré.")
            log_employee_action(request, 'BREAK_START', f"Début de pause enregistré à {now_dt.strftime('%H:%M:%S')}")
            
    elif action == 'break_end':
        if not attendance.break_start:
            messages.error(request, "Vous n'êtes pas en pause.")
        elif attendance.break_end:
            messages.warning(request, "Vous avez déjà repris votre service.")
        else:
            attendance.break_end = now_dt
            # Restaurer le statut d'origine (LATE ou PRESENT)
            attendance.status = 'LATE' if attendance.is_late else 'PRESENT'
            attendance.save()
            messages.success(request, "Reprise de service enregistrée.")
            log_employee_action(request, 'BREAK_END', f"Reprise de service enregistrée à {now_dt.strftime('%H:%M:%S')}")
            
    elif action == 'out':
        if not attendance.clock_in:
            messages.error(request, "Vous devez d'abord pointer votre arrivée.")
        elif attendance.clock_out:
            messages.warning(request, "Vous avez déjà pointé votre départ aujourd'hui.")
        else:
            # Si l'employé était en pause non clôturée, on la ferme automatiquement
            if attendance.break_start and not attendance.break_end:
                attendance.break_end = now_dt
                
            attendance.clock_out = now_dt
            attendance.status = 'CLOCK_OUT'
            if lat and lng:
                attendance.latitude_out = lat
                attendance.longitude_out = lng
            attendance.save()
            messages.success(request, f"Service terminé. Durée travaillée : {attendance.total_work_hours} heures.")
            log_employee_action(request, 'CLOCK_OUT', f"Pointage de départ enregistré à {now_dt.strftime('%H:%M:%S')} (GPS: {lat or 'N/D'}, {lng or 'N/D'} | Durée : {attendance.total_work_hours} heures)")
            
    return redirect('hotel_dashboard')


@login_required
@hotel_required
def hotel_schedule_save(request):
    """
    Enregistre ou met à jour le planning hebdomadaire d'un collaborateur.
    """
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les administrateurs de l'hôtel peuvent modifier le planning.")
        return redirect('hotel_dashboard')
        
    hotel = request.user
    
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        agent = get_object_or_404(User, id=agent_id, parent_hotel=hotel, role='AGENT')
        
        # Supprimer le planning existant pour cet agent avant de recréer
        EmployeeSchedule.objects.filter(employee=agent).delete()
        
        days_added = 0
        for day_val in range(1, 8):
            enabled = request.POST.get(f'day_{day_val}_enable')
            if enabled:
                start_str = request.POST.get(f'day_{day_val}_start')
                end_str = request.POST.get(f'day_{day_val}_end')
                
                if start_str and end_str:
                    try:
                        start_time = datetime.datetime.strptime(start_str, "%H:%M").time()
                        end_time = datetime.datetime.strptime(end_str, "%H:%M").time()
                        
                        EmployeeSchedule.objects.create(
                            hotel=hotel,
                            employee=agent,
                            day_of_week=day_val,
                            start_time=start_time,
                            end_time=end_time
                        )
                        days_added += 1
                    except Exception as e:
                        pass
        
        messages.success(request, f"Planning mis à jour avec succès ({days_added} jours configurés).")
        
    return redirect('hotel_sub_agents')


@login_required
@hotel_required
def hotel_task_assign(request):
    """
    Assigne une tâche exceptionnelle à un réceptionniste/collaborateur.
    """
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les gérants de l'hôtel peuvent assigner des tâches.")
        return redirect('hotel_dashboard')
        
    hotel = request.user
    
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date_str = request.POST.get('due_date')
        
        agent = get_object_or_404(User, id=agent_id, parent_hotel=hotel, role='AGENT')
        
        if title and due_date_str:
            try:
                due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                EmployeeTask.objects.create(
                    hotel=hotel,
                    employee=agent,
                    title=title,
                    description=description or '',
                    due_date=due_date
                )
                messages.success(request, f"Tâche exceptionnelle assignée avec succès à {agent.get_full_name()} !")
            except Exception as e:
                messages.error(request, f"Erreur lors de l'enregistrement de la tâche : {e}")
        else:
            messages.error(request, "Veuillez renseigner un titre et une date d'échéance.")
            
    return redirect('hotel_sub_agents')


@login_required
@hotel_required
def hotel_task_complete(request, task_id):
    """
    Valide l'achèvement d'une tâche exceptionnelle.
    """
    hotel = request.user
    
    # Si c'est un agent, on valide qu'il en est bien le destinataire
    if hasattr(request, 'actual_user'):
        task = get_object_or_404(EmployeeTask, id=task_id, hotel=hotel, employee=request.actual_user)
    else:
        task = get_object_or_404(EmployeeTask, id=task_id, hotel=hotel)
        
    task.status = 'COMPLETED'
    task.completed_at = timezone.now()
    task.save()
    
    # Notification email au gérant de l'hôtel
    try:
        from logertogo.emails import send_employee_task_completed_notification
        send_employee_task_completed_notification(task.hotel, task.employee, task)
    except Exception as email_err:
        import logging
        logging.getLogger('django').error(f"❌ [EMAIL ERROR] Erreur envoi completion tâche : {email_err}")
        
    log_employee_action(request, 'TASK_COMPLETE', f"Consigne exceptionelle validée : '{task.title}'")
    messages.success(request, f"Tâche '{task.title}' validée et marquée comme terminée !")
    return redirect('hotel_dashboard')


# --- Dynamic Subdomain Error Handlers ---

def hotel_404_handler(request, exception):
    return render(request, 'hotel/404.html', status=404)

def hotel_500_handler(request):
    return render(request, 'hotel/500.html', status=500)
