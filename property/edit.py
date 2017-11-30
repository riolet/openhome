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
            errors.append("Cannot find listing to update. Try saving your edits and refreshing the page.")
            return

        if not self.item_is_owned(parent):
            errors.append("Not authorized to edit this listing")
            return

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
        elif model == 'suiteroom':
            new_component = SuiteRoom.construct_default(parent)
        else:
            errors.append('Cannot create a {} for your listing.'.format(model))
            return

        try:
            new_component.full_clean()
            new_component.save()
        except Exception as e:
            errors.append("Error creating {}: {}".format(model, e))
            return

        print("Adding {} to {}".format(model, parent))
        successes['action'] = 'added'
        successes['model'] = model
        successes['pk'] = new_component.id
        return

    def remove_component(self, model, key, errors, successes):
        try:
            if model == 'property':
                deathrow = Property.objects.get(pk=key)
            elif model == 'lot':
                deathrow = Lot.objects.get(pk=key)
            elif model == 'house':
                deathrow = House.objects.get(pk=key)
            elif model == 'suite':
                deathrow = Suite.objects.get(pk=key)
            elif model == "suiteroom":
                deathrow = SuiteRoom.objects.get(pk=key)
            elif model == "houseroom":
                deathrow = HouseRoom.objects.get(pk=key)
            elif model == "structure":
                deathrow = Structure.objects.get(pk=key)
            else:
                errors.append('Cannot delete the {} in your listing.'.format(model))
                return
        except (Suite.DoesNotExist, Lot.DoesNotExist, House.DoesNotExist):
            errors.append("Cannot find listing to remove. Try saving your edits and refreshing the page.")
            return

        if not self.item_is_owned(deathrow):
            errors.append("Not authorized to edit this listing")
            return

        print("Removing {} with id {}".format(model, key))
        deathrow.delete()
        successes['action'] = 'removed'
        successes['model'] = model
        successes['pk'] = key
        return

    def update_component(self, model, errors, successes, pk, **updates):
        try:
            if model == 'property':
                comp = Property.objects.get(pk=pk)
            elif model == 'lot':
                comp = Lot.objects.get(pk=pk)
            elif model == 'house':
                comp = House.objects.get(pk=pk)
            elif model == 'suite':
                comp = Suite.objects.get(pk=pk)
            elif model == "structure":
                comp = Structure.objects.get(pk=pk)
            else:
                errors.append('Cannot update the {} in your listing.'.format(model))
                return
        except (Suite.DoesNotExist, Lot.DoesNotExist, House.DoesNotExist):
            errors.append("Cannot find listing to edit. Try refreshing the page.")
            return

        if not self.item_is_owned(comp):
            errors.append("Not authorized to edit this listing")
            return

        try:
            comp.update(updates)
            comp.normalize_fields()
            comp.full_clean()
            comp.save()
        except Exception as e:
            errors.append("{}".format(e))
            return

        successes['type'] = model
        successes['pk'] = pk
        # successes['updated_model'] = serializers.serialize('json', obj)
        successes['updated_model'] = comp.export()

    def update_rooms(self, model, errors, successes, pk, **updates):
        try:
            if model == 'houseroom':
                comp = House.objects.get(pk=pk)
            elif model == 'suiteroom':
                comp = Suite.objects.get(pk=pk)
            else:
                errors.append('Cannot update the {} in your listing.'.format(model))
                return
        except (Suite.DoesNotExist, Lot.DoesNotExist, House.DoesNotExist):
            errors.append("Cannot find listing to edit. Try refreshing the page.")
            return

        if not self.item_is_owned(comp):
            errors.append("Not authorized to edit this listing")
            return

        # updates at this point looks like:
        #{'11_floor': '1',
        # '11_role': 'unspecified',
        # '11_square_meters': '2',
        # '12_floor': '1',
        # '12_role': 'unspecified',
        # '12_square_meters': '4',
        # 'type': 'houseroom'}
        print("updates: {}".format(updates))
        keys = [k.partition("_")[0] for k in updates.keys()]
        print("keys A: {}".format(keys))
        keys = {k for k in keys if k.isnumeric()}
        print("keys B: {}".format(keys))
        room_updates = {}
        for key in keys:
            if model == 'houseroom':
                room = HouseRoom.objects.get(pk=key)
                if room.house != comp:
                    errors.append("Not authorized to edit room {}".format(key))
                    continue
            elif model == 'suiteroom':
                room = SuiteRoom.objects.get(pk=key)
                if room.suite != comp:
                    errors.append("Not authorized to edit room {}".format(key))
                    continue
            fixed_params = {
                'floor': updates.get("{}_floor".format(key), room.floor),
                'square_meters': updates.get("{}_square_meters".format(key), room.square_meters),
                'role': updates.get("{}_role".format(key), room.role)
            }
            print("\nfor loop updates: {}".format(updates))
            print("\nfixed params: {}".format(fixed_params))
            room.update(fixed_params)
            room.normalize_fields()
            room.full_clean()
            room.save()
            room_updates[key] = room.export()

        successes['type'] = model
        successes['pk'] = pk
        successes['updated_rooms'] = room_updates

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
        do_stamp_update = True
        request_type = decoded.get('type', 'error')
        if request_type == 'action':
            action_type = decoded.get('action', 'error')
            if action_type == 'add':
                self.add_component(model=decoded['model'], parent_id=decoded['pk'], errors=errors, successes=successes)
            elif action_type == 'remove':
                self.remove_component(model=decoded['model'], key=decoded['pk'], errors=errors, successes=successes)
                # if deleting the whole listing, don't update the timestamp on it.
                do_stamp_update = (decoded['model'] != 'property')
            else:
                errors.append('Error. Did not understand action {}'.format(action_type))
        elif request_type in ['property', 'lot', 'structure', 'house', 'suite']:
            self.update_component(model=request_type, errors=errors, successes=successes, **decoded)
        elif request_type in ['houseroom', 'suiteroom']:
            self.update_rooms(model=request_type, errors=errors, successes=successes, **decoded)
        else:
            errors.append('Error. Did not understand request type {}'.format(decoded['type']))

        # update the edit date stamp
        if do_stamp_update:
            self.property.edit_stamp = timezone.now()
            self.property.save()

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