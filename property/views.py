from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from .login import login, logout

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


def account(request):
    if request.session.get('logged_in', False) is not True:
        return HttpResponse('User is not logged in. <a href="/login/">login</a>')

    # user IS logged in.
    user_id = request.session.get('login_email', 'NO@EMAIL.COM')
    if request.method == 'POST':
        return HttpResponse("Logged in. Update user {} information in database".format(user_id))
    else:
        return HttpResponse("Logged in. Show/edit contact info for user {}'s listed properties.".format(user_id))
