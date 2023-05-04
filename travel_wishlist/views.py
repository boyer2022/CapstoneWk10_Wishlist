from django.shortcuts import render, redirect,  get_object_or_404
from django.conf.urls import url
from .models import Place
from .forms import NewPlaceForm, TripReviewForm

# Log in decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

# Create your views here.
@login_required
def place_list(request):
    if request.method == 'POST':
        # create new place
        form = NewPlaceForm(request.POST)   # Creating a form from data in the request
        place = form.save(commit=False)                 # .save() is making a model object
        place.user = request.user           # Associate the place with the current logged-in user

        if form.is_valid():                 # if valid - validation against DB constraints
            place.save()                    # saves place to DB
            return redirect('place_list')   # Reloads home page

    # Making call to DB
        # Fetches ALL of the places(objects) from DB
    # places = Place.objects.all()
            # OR
    places = Place.objects.filter(user=request.user).filter(visited=False).order_by('name')
    new_place_form = NewPlaceForm()         # Used to create HTML
    return render(request, 'travel_wishlist/wishlist.html', {'places': places, 'new_place_form': new_place_form})

@login_required
# Views function
def places_visited(request):
    visited = Place.objects.filter(visited=True)    # Query to the database
    return render(request, 'travel_wishlist/visited.html', { 'visited': visited })


@login_required
def place_was_visited(request, place_pk):           # place_pk is a variable from url.py
    # Only responds to POST requests
    if request.method == 'POST':
        # place = Place.objects.get(pk=place_pk)
        place = get_object_or_404(Place, pk=place_pk)       # 404 error- Use Dev tools as Network-fetch, paste in Console, change pk to incorrect number, 'Enter'
        if place.user == request.user:                      # only let a user visit their own places
            place.visited = True
            place.save()                                # Saves to DB, must be saved to  be in DB
        else:
            return HttpResponseForbidden()
        
    return redirect('place_list')

@login_required
def delete_place(request, place_pk):
    place = get_object_or_404(Place, pk=place_pk)
    if place.user == request.user:
        place.delete()
        return redirect('place_list')
    else:
        return HttpResponseForbidden() 
    
@login_required
def place_details(request, place_pk):

    place = get_object_or_404(Place, pk=place_pk)

    if place.user != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = TripReviewForm(request.POST, request.FILES, instance=place)  # instance = model object to update with the form data
        if form.is_valid():
            form.save()
            messages.info(request, 'Trip information updated!')
        else:
            messages.error(request, form.errors)  # Temp error message - future version should improve 

        return redirect('place_details', place_pk=place_pk)

    else:    # GET place details
        if place.visited:
            review_form = TripReviewForm(instance=place)  # Pre-populate with data from this Place instance
            return render(request, 'travel_wishlist/place_detail.html', {'place': place, 'review_form': review_form} )

        else:
            return render(request, 'travel_wishlist/place_detail.html', {'place': place} )


@login_required
# Requested from about.html
def about(request):
    author = 'Matt'
    about = "A website to create a list of places to visit"
    return render(request, 'travel_wishlist/about.html', {'author': author, 'about': about})


