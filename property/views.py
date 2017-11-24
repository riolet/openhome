from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return HttpResponse("Index page. List of recently added properties.")

def search_results(request):
    return HttpResponse("Search page. Specify filters and see results.")

def search(request):
    return HttpResponse("headless. get search results")

def details(request):
    return HttpResponse("show details of property")

def new(request):
    return HttpResponse("form to create new property listing")

def create(request):
    return HttpResponse("headless (from new) - create new property")

def edit(request):
    return HttpResponse("form to edit property listing")

def update_listing(request):
    return HttpResponse("headless (from edit) - update property details")

def remove(request):
    return HttpResponse("delete a listing")

def login(request):
    return HttpResponse("Login via rioauth (opt. via google or github)")

def logout(request):
    return HttpResponse("headless. logout and redirect to home")

def user(request):
    return HttpResponse("Show/edit contact info and this user's listed properties.")

def update_user(request):
    return HttpResponse()
