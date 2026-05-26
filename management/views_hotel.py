from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.core.validators import MinValueValidator
from django.urls import reverse
from users.models import User
from .models import HotelRoom, HotelBooking, HotelChargeItem
import datetime
from decimal import Decimal

# Custom decorator for hotel staff access
def hotel_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('hotel_login')
        if request.user.role not in ['HOTEL', 'AUBERGE', 'SUB_ADMIN']:
            messages.error(request, "Accès restreint aux professionnels de l'hôtellerie.")
            return redirect('hotel_promo')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def hotel_promo(request):
    """
    Landing page for hotels.logertogo.com showing the hotel management software.
    """
    if request.user.is_authenticated and request.user.role in ['HOTEL', 'AUBERGE']:
        return redirect('hotel_dashboard')
    return render(request, 'hotel/hotel_promo.html')

def hotel_login(request):
    """
    Log in an hotel owner / manager.
    """
    if request.user.is_authenticated and request.user.role in ['HOTEL', 'AUBERGE']:
        return redirect('hotel_dashboard')
        
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        user = authenticate(request, phone_number=phone, password=password)
        if user is not None:
            if user.role in ['HOTEL', 'AUBERGE', 'SUB_ADMIN']:
                login(request, user)
                messages.success(request, f"Bienvenue, {user.company_name or 'Hôtelier Loger Togo'} !")
                return redirect('hotel_dashboard')
            else:
                messages.error(request, "Ce compte n'est pas un profil Hôtel ou Auberge.")
        else:
            messages.error(request, "Identifiants invalides.")
            
    return render(request, 'hotel/login.html')

def hotel_register(request):
    """
    Sign up a new hotel / auberge.
    """
    if request.user.is_authenticated and request.user.role in ['HOTEL', 'AUBERGE']:
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
                    is_saas_active=True # Activé par défaut pour test
                )
                login(request, user)
                messages.success(request, "Votre compte Hôtel/Auberge a été créé avec succès !")
                return redirect('hotel_dashboard')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'inscription : {e}")
                
    return render(request, 'hotel/register.html')

def hotel_logout(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('hotel_promo')

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
        
        if HotelRoom.objects.filter(hotel=request.user, room_number=number).exists():
            messages.error(request, f"La chambre {number} existe déjà.")
        else:
            try:
                HotelRoom.objects.create(
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
                    balcony=balcony
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
        
        try:
            room.save()
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
            
            # Amount calculations
            if rate_type == 'HOURLY' and room.price_per_hour:
                qty = int(hours_qty)
                amount_due = room.price_per_hour * qty
            else:
                nights = (check_out.date() - check_in.date()).days
                if nights <= 0:
                    nights = 1 # Minimum 1 night
                amount_due = room.price_per_night * nights
                
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
                status='PENDING'
            )
            
            messages.success(request, f"Réservation créée avec succès pour {name} !")
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
        # Ensure outstanding balance is fully paid (or record what they paid)
        final_payment = Decimal(request.POST.get('final_payment', 0))
        booking.amount_paid += final_payment
        booking.status = 'CHECKED_OUT'
        booking.save()
        
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
            
            # Update extra_charges in booking
            booking.extra_charges += charge.total_price
            booking.save()
            
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
        
        try:
            hotel.save()
            messages.success(request, "Informations de l'établissement mises à jour avec succès !")
        except Exception as e:
            messages.error(request, f"Erreur : {e}")
            
    return render(request, 'hotel/hotel_profile.html')


# --- Dynamic Subdomain Error Handlers ---

def hotel_404_handler(request, exception):
    return render(request, 'hotel/404.html', status=404)

def hotel_500_handler(request):
    return render(request, 'hotel/500.html', status=500)
