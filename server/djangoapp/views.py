from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from .models import CarDealer, CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, get_dealer_by_id_from_cf, get_dealers_by_state
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method =="GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["pwd"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["pwd"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        user_exist = False

        try: 
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug(f"{username} is new user")

        if not user_exist:
            user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "User already exists"
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://bluicien-3000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships

        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        context["dealer_id"] = dealer_id

        review_url = "https://bluicien-5000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
        reviews = get_dealer_reviews_from_cf(review_url, dealer_id)
        context["reviews_list"] = reviews

        dealer_url = "https://bluicien-3000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id=dealer_id)
        context["dealer"] = dealer

        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        if request.method == "GET":
            context = {}
            cars = list(CarModel.objects.filter(dealer_id=dealer_id))
            for car in cars:
                car.year = car.year.strftime("%Y")
            context["cars"] = cars

            dealer_url = "https://bluicien-3000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
            dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id=dealer_id)  

            context["dealer"] = dealer
            context["dealer_id"] = dealer_id

            return render(request, "djangoapp/add_review.html", context)

        if request.method == "POST":
            user = request.user
            review = {}
            review["id"] = dealer_id
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = f"{user.first_name} {user.last_name}"
            review["dealership"] = dealer_id
            review["review"] = request.POST['content']
            checked = request.POST.get('purchasecheck', False)

            if checked == "on":
                checked = True
            review["purchase"] = checked
            review["purchase_date"] = request.POST['purchasedate']
            car_make, car_model, car_year = request.POST['car_details'].split("-")
            review["car_make"] = car_make
            review["car_model"] = car_model
            review["car_year"] = car_year
            url = "https://bluicien-5000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
            json_payload = {}
            json_payload["review"] = review
            post_request(url, json_payload, dealerId=dealer_id)
            print("Review submitted.")

            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
            
    else: 
        print("User is not authenticated")
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
