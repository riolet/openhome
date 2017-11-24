from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic

from .models import Property


class HomeView(generic.ListView):
    template_name = 'property/home.html'
    context_object_name = 'latest_property_list'

    def get_queryset(self):
        # The 5 most recently published properties
        return Property.objects.order_by('-publish_stamp')[:5]


class DetailView(generic.DetailView):
    model = Property
    template_name = 'property/detail.html'


def search_results(request):
    return HttpResponse("Search page. Specify filters and see results.")


def search(request):
    return HttpResponse("headless. get search results")


def new(request):
    if request.method == 'POST':
        return HttpResponse("create new property listing in database")
    else:
        return HttpResponse("form to create new property listing")


def edit(request, property_id):
    if request.method == 'POST':
        return HttpResponse("Update property listing {} in database".format(property_id))
    elif request.method == 'DELETE':
        return HttpResponse("Deleting property listing {} from database".format(property_id))
    else:
        return HttpResponse("Getting form to edit property listing {}".format(property_id))


def login(request):
    return HttpResponse("Login via rioauth (opt. via google or github)")


def logout(request):
    return HttpResponse("headless. logout and redirect to home")


def user(request, user_id):
    if request.method == 'POST':
        return HttpResponse("Update user {} information in database".format(user_id))
    else:
        return HttpResponse("Show/edit contact info for user {}'s listed properties.".format(user_id))
