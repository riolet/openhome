from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from .login import login, logout

from .models import Property, User


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
    """
    rendering property/account.html
        requires a 'user' object
        may include: info_message, error_message
    """
    if request.session.get('logged_in', False) is not True:
        return HttpResponse('User is not logged in. <a href="/login/">login</a>')

    # user IS logged in.
    user_id = request.session.get('login_email', 'NO@EMAIL.COM')
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        import pprint
        print("post data:")
        pprint.pprint(request.POST)
        new_email = request.POST.get('email', user.email)
        new_phone = request.POST.get('phone', user.phone)
        new_fax = request.POST.get('fax', user.fax)
        new_mail = request.POST.get('mail', user.mail)
        new_message = request.POST.get('message', user.message)
        new_b_email = request.POST.get('b_email', False)
        new_b_phone = request.POST.get('b_phone', False)
        new_b_fax = request.POST.get('b_fax', False)
        new_b_mail = request.POST.get('b_mail', False)

        new_b_email = new_b_email in (True, 'on')
        new_b_phone = new_b_phone in (True, 'on')
        new_b_fax = new_b_fax in (True, 'on')
        new_b_mail = new_b_mail in (True, 'on')

        user.email = new_email
        user.phone = new_phone
        user.fax = new_fax
        user.mail = new_mail
        user.message = new_message
        user.b_email = new_b_email
        user.b_phone = new_b_phone
        user.b_fax = new_b_fax
        user.b_mail = new_b_mail
        user.save()

        return render(request, 'property/account.html', {
            'user': user,
            'info_message': "User updated successfully.",
        })
    else:
        return render(request, 'property/account.html', {
            'user': user,
        })
