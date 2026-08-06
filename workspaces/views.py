from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Max, Min
from .models import CoWorkingSpace, WorkspaceUnit, Amenity

def space_list_view(request):
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    capacity = request.GET.get('capacity', '')
    max_price = request.GET.get('max_price', '')
    unit_type = request.GET.get('unit_type', '')
    selected_amenities = request.GET.getlist('amenities')

    spaces = CoWorkingSpace.objects.all().prefetch_related('units', 'amenities')

    # Basic Text Search
    if query:
        spaces = spaces.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(address__icontains=query)
        )

    # City filter
    if city:
        spaces = spaces.filter(city__iexact=city)

    # Capacity Filter (find spaces having a unit that can fit this capacity)
    if capacity:
        try:
            cap_val = int(capacity)
            spaces = spaces.filter(units__seating_capacity__gte=cap_val, units__is_active=True).distinct()
        except ValueError:
            pass

    # Budget Filter (price per day)
    if max_price:
        try:
            price_val = float(max_price)
            spaces = spaces.filter(units__price_per_day__lte=price_val, units__is_active=True).distinct()
        except ValueError:
            pass

    # Unit type filter
    if unit_type:
        spaces = spaces.filter(units__type=unit_type, units__is_active=True).distinct()

    # Amenities filter (space must have all selected amenities)
    if selected_amenities:
        for amenity_id in selected_amenities:
            spaces = spaces.filter(amenities__id=amenity_id)

    # Gather metadata for search form
    cities = CoWorkingSpace.objects.values_list('city', flat=True).distinct()
    all_amenities = Amenity.objects.all()

    # Decorate spaces with custom match indicators for UX
    for space in spaces:
        # Calculate a match score based on how many amenities and requirements it satisfies
        score = 100
        reasons = []
        if capacity:
            matching_units = space.units.filter(seating_capacity__gte=int(capacity))
            if not matching_units.exists():
                score -= 30
                reasons.append("Capacity requirement partially met by combining desks")
            else:
                reasons.append("Has workspaces fitting your team size exactly")
        else:
            reasons.append("Matches general seating")

        if max_price:
            affordable_units = space.units.filter(price_per_day__lte=float(max_price))
            if not affordable_units.exists():
                score -= 30
                reasons.append("Slightly exceeds ideal budget")
            else:
                reasons.append("Within budget limits")
                
        space.match_score = max(0, score)
        space.match_reasons = reasons[:2]

    context = {
        'spaces': spaces,
        'cities': cities,
        'all_amenities': all_amenities,
        'selected_amenities': [int(a) for a in selected_amenities if a.isdigit()],
        'query': query,
        'city': city,
        'capacity': capacity,
        'max_price': max_price,
        'unit_type': unit_type,
    }
    return render(request, 'workspaces/search.html', context)

def space_detail_view(request, pk):
    space = get_object_or_404(CoWorkingSpace.objects.prefetch_related('units', 'amenities', 'reviews__user'), pk=pk)
    units = space.units.filter(is_active=True)
    reviews = space.reviews.all().order_by('-created_at')
    
    can_review = False
    if request.user.is_authenticated:
        from bookings.models import Booking
        can_review = Booking.objects.filter(
            user=request.user,
            unit__space=space,
            status='APPROVED'
        ).exists()
        
    context = {
        'space': space,
        'units': units,
        'unit_types': WorkspaceUnit.UNIT_TYPES,
        'reviews': reviews,
        'can_review': can_review,
    }
    return render(request, 'workspaces/detail.html', context)

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review

@login_required
def submit_review_view(request, space_id):
    if request.method == 'POST':
        space = get_object_or_404(CoWorkingSpace, pk=space_id)
        rating_str = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        try:
            rating = int(rating_str)
            if rating < 1 or rating > 5:
                raise ValueError()
        except (ValueError, TypeError):
            messages.error(request, "Invalid rating selected.")
            return redirect('space_detail', pk=space_id)
            
        # Check if the user has booked this space
        from bookings.models import Booking
        has_booked = Booking.objects.filter(
            user=request.user,
            unit__space=space,
            status='APPROVED'
        ).exists()
        
        if not has_booked:
            messages.error(request, "You can only review workspaces you have had an approved booking with.")
            return redirect('space_detail', pk=space_id)
            
        Review.objects.create(
            space=space,
            user=request.user,
            rating=rating,
            comment=comment
        )
        
        # Notify the owner about the new review
        from accounts.models import Notification
        Notification.objects.create(
            user=space.owner,
            title="New Review Received",
            message=f"Your space '{space.name}' received a {rating}-star review from {request.user.username}."
        )
        
        messages.success(request, "Thank you! Your review has been submitted successfully.")
        
    return redirect('space_detail', pk=space_id)

