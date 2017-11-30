import json
from django.http import HttpRequest, HttpResponseForbidden, JsonResponse
from django.core import serializers
from django.shortcuts import get_object_or_404, render
from property.models import *


def edit(request, property_id):
    """
    :type request: HttpRequest
    """
    user_id = request.session.get('login_email', '')
    user = get_object_or_404(User, pk=user_id.lower())
    property = get_object_or_404(Property, pk=property_id)
    if property.owner != user:
        return HttpResponseForbidden()

    e_model = EditView(request, property_id)

    if request.method == 'POST':
        return e_model.post_method()
    else:
        return e_model.get_method()

# models:
#
#       Property
#    /     |     \
# Lot | House | Suite
# Stct| HRoom | SRoom
#
class EditView:
    def __init__(self, request, property_id):
        self.request = request
        self.session = request.session
        self.property_id = property_id
        self.user_id = self.session.get('login_email', '').lower()

        self.user = User.objects.get(pk=self.user_id)
        self.property = Property.objects.get(pk=self.property_id)

    def item_is_owned(self, model_object):
        if isinstance(model_object, Property):
            return model_object == self.property
        elif model_object._meta.model_name in ['lot', 'house', 'suite']:
            return self.item_is_owned(model_object.property)
        elif isinstance(model_object, Structure):
            return self.item_is_owned(model_object.lot)
        elif isinstance(model_object, HouseRoom):
            return self.item_is_owned(model_object.house)
        elif isinstance(model_object, SuiteRoom):
            return self.item_is_owned(model_object.suite)
        else:
            return False

    def add_component(self, model, parent_id, errors, successes):
        # get parent
        # add new child
        # save it all
        # set successes
        try:
            if model in ['lot', 'house', 'suite']:
                parent = self.property
            elif model == "suiteroom":
                parent = Suite.objects.get(pk=parent_id)
            elif model == "houseroom":
                parent = House.objects.get(pk=parent_id)
            elif model == "structure":
                parent = Lot.objects.get(pk=parent_id)
            else:
                errors.append('Cannot add a {} to your listing.'.format(model))
                return
        except (Suite.DoesNotExist, Lot.DoesNotExist, House.DoesNotExist):
            errors.append("Cannot listing to update. Try saving your edits and refreshing the page.")
            return

        if not self.item_is_owned(parent):
            errors.append("Not authorized to edit this listing")
            return

        print("Adding {} to {}".format(model, parent))
        new_component = None
        if model == 'lot':
            new_component = Lot.construct_default(parent)
        elif model == 'house':
            new_component = House.construct_default(parent)
        elif model == 'suite':
            new_component = Suite.construct_default(parent)
        elif model == 'structure':
            new_component = Structure.construct_default(parent)
        elif model == 'houseroom':
            new_component = HouseRoom.construct_default(parent)
        elif model == 'suiterooom':
            new_component = SuiteRoom.construct_default(parent)
        else:
            errors.append('Cannot add a {} to your listing.'.format(model))
            return

        try:
            new_component.full_clean()
            new_component.save()
        except Exception as e:
            errors.append("Error creating {}: {}".format(model, e))
            return


        successes['action'] = 'added'
        successes['model'] = model
        successes['pk'] = new_component.id
        return

    def post_method(self):
        if self.property.owner != self.user:
            return HttpResponseForbidden()

        str_request = self.request.body.decode('utf-8')
        decoded = json.loads(str_request)
        # request will be a JSON dictionary.
        #   if .type is "action"
        #     .action will be "add" or "remove"
        #     .model will be the model type to add/remove
        #     .pk will be the key to delete or parent id
        #   elif .type is a model
        #     .pk will be the key
        #     and other fields will be model fields
        # response will be a JSON response including:
        #   - success/failure of action
        #   - primary key of any new object
        errors = []
        successes = {}
        request_type = decoded.get('type', 'error')
        if request_type == 'action':
            action_type = decoded.get('action', 'error')
            if action_type == 'add':
                self.add_component(model=decoded['model'], parent_id=decoded['pk'], errors=errors, successes=successes)
            elif action_type == 'remove':
                # TODO: SECURITY: verify permissions to perform removal
                print("Removing {} with id {}".format(decoded['model'], decoded['pk']))
                successes['action'] = 'removed'
                successes['model'] = decoded['model']
                successes['pk'] = decoded['pk']
            else:
                errors.append('Error. Did not understand action {}'.format(action_type))
        elif request_type in ['property', 'lot', 'structure', 'house', 'houseroom', 'suite', 'suiteroom']:
            # TODO: SECURITY: verify permissions to perform update
            print("Updating {} with id {}".format(request_type, decoded['pk']))
            successes['type'] = decoded['type']
            successes['pk'] = decoded['pk']
            # successes['updated_model'] = serializers.serialize('json', obj)
            successes['updated_model'] = '[{}]'
        else:
            errors.append('Error. Did not understand request type {}'.format(decoded['type']))

        # data = {}
        # data['something'] = 'useful'
        # return JsonResponse(data)
        #    or
        # houses = Property.house_set.all()
        # data = serializers.serialize("json", houses)
        # return HttpResponse(data, content_type='application/json')
        response = {
            'result': 'error' if errors else 'success',
            'errors': errors,
            'successes': successes
        }
        return JsonResponse(response)

    def get_method(self):
        if self.property.owner != self.user:
            return HttpResponseForbidden()

        return render(self.request, 'property/edit.html', {
            'user': self.user,
            'property': self.property,
            'country_choices': Property.COUNTRIES,
            'status_choices': Property.STATUS,
            'province_choices': Property.PROVINCES,
            'garage_choices': House.GARAGES
        })