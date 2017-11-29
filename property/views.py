from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic
from django.utils import timezone
from .login import login, logout

from .models import *


class HomeView(generic.ListView):
    template_name = 'property/home.html'
    context_object_name = 'latest_property_list'

    def get_queryset(self):
        # The 5 most recently published properties
        return Property.objects.order_by('-publish_stamp').filter(Q(status='A') | Q(status='P'))[:10]


class DetailView(generic.DetailView):
    model = Property
    template_name = 'property/detail.html'


def search_results(request):
    return render(request, 'property/results.html')


def search(request):
    return HttpResponse("headless. get search results")


def new(request):
    user_id = request.session.get('login_email', '')
    user = get_object_or_404(User, pk=user_id.lower())

    if request.method == 'POST':
        import pprint
        pprint.pprint(dict(request.POST))

        description = request.POST.get('description', '')
        price = request.POST.get('price', '1')
        property_tax = request.POST.get('property_tax', '1')
        property_type = request.POST.get('property_type', '')
        country = request.POST.get('country', 'CAN')
        province = request.POST.get('province', 'BC')
        region = request.POST.get('region', '')
        city = request.POST.get('city', '')
        neighborhood = request.POST.get('neighborhood', '')
        street_address = request.POST.get('street_address', '')
        postal_code = request.POST.get('postal_code', '')
        latitude = request.POST.get('latitude', '')
        longitude = request.POST.get('longitude', '')

        p = Property(
            owner=user,
            creation_stamp=timezone.now(),
            publish_stamp=None,
            edit_stamp=timezone.now(),
            status='U',
            description=description,
            price=price,
            property_tax=property_tax,
            property_type=property_type,
            country=country,
            province=province,
            region=region,
            city=city,
            neighborhood=neighborhood,
            street_address=street_address,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude
        )

        p.normalize_fields()
        p.escape_fields()
        try:
            p.full_clean(exclude=['id'])
        except ValidationError as e:
            return render(request, 'property/new.html', {
                'user': user,
                'country_choices': Property.COUNTRIES,
                'status_choices': Property.STATUS,
                'province_choices': Property.PROVINCES,
                'errors': e.message_dict,
                'property': p
            })
        p.id = p.generate_id()
        p.save()
        return HttpResponseRedirect(reverse('property:edit', args=(p.id,)))
    else:
        return render(request, 'property/new.html', {
            'user': user,
            'country_choices': Property.COUNTRIES,
            'status_choices': Property.STATUS,
            'province_choices': Property.PROVINCES,
        })


def edit(request, property_id):
    user_id = request.session.get('login_email', '')
    user = get_object_or_404(User, pk=user_id.lower())
    property = get_object_or_404(Property, pk=property_id)
    if property.owner != user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        # request will be a JSON action dictionary.
        # actions may be:
        #   - update (object_id, key:values)
        #   - add (parent, object_type)
        #   - remove (object_id)
        # response will be a JSON response including:
        #   - success/failure of action
        #   - primary key of any new object
        return HttpResponse("Update property listing {} in database".format(property_id))
    else:
        return render(request, 'property/edit.html', {
            'user': user,
            'property': property,
            'country_choices': Property.COUNTRIES,
            'status_choices': Property.STATUS,
            'province_choices': Property.PROVINCES,
            'garage_choices': House.GARAGES
        })


def delete(request, property_id):
    # validate user owns property listing
    # remove property
    #
    if request.method == 'POST':
        return HttpResponse("Deleting property listing {} from database".format(property_id))
    else:
        return HttpResponseRedirect(reverse('property:home'))


def account(request):
    """
    rendering property/account.html
        requires a 'user' object
        may include: info_message, error_message
    """
    if request.session.get('logged_in', False) is not True:
        return HttpResponse('User is not logged in. <a href="/login/">login</a>')

    # user IS logged in.
    user_id = request.session.get('login_email', '')
    user = get_object_or_404(User, pk=user_id.lower())
    if request.method == 'POST':
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
