import random
from django.db import models


class Property(models.Model):
    STATUS = (
        ('U', 'Unpublished'),
        ('S', 'Sold'),
        ('A', 'Available'),
        ('R', 'Removed'),
        ('P', 'Pending Sale'),
    )
    PROVINCES = (
        ('NL', 'Newfoundland and Labrador'),
        ('PE', 'Prince Edward Island'),
        ('NS', 'Nova Scotia'),
        ('NB', 'New Brunswick'),
        ('QC', 'Quebec'),
        ('ON', 'Ontario'),
        ('MB', 'Manitoba'),
        ('SK', 'Saskatchewan'),
        ('AB', 'Alberta'),
        ('BC', 'British Columbia'),
        ('YT', 'Yukon'),
        ('NT', 'Northwest Territories'),
        ('NU', 'Nunavut'),
    )
    COUNTRIES = (
        ('CAN', 'Canada'),
    )

    # Primary key.
    # id postal code (6), date stamp (5), alphanum serial padding out to 20 chars
    id = models.CharField(max_length=20, primary_key=True)

    # owner = models.ForeignKey(Users, on_delete=models.SET_NULL)
    creation_stamp = models.DateTimeField('creation time')
    publish_stamp = models.DateTimeField('publish time', null=True, default=None)
    edit_stamp = models.DateTimeField('latest edit time')
    status = models.CharField(max_length=1, choices=STATUS)
    description = models.TextField()
    price = models.FloatField()
    property_tax = models.FloatField()
    property_type = models.CharField(max_length=50)

    # Location information
    country = models.CharField(max_length=3, choices=COUNTRIES)
    province = models.CharField(max_length=2, choices=PROVINCES)
    region = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    community = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=6)
    # lat/long at 6 decimal places = 1.113m precision.
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def generate_id(self):
        p_code = str(self.postal_code)
        d_stamp = str(int(self.creation_stamp.timestamp() // 86400))  # 86400 is seconds/day
        prefix = p_code + d_stamp
        # TODO: get next in sequence for given prefix instead of random
        prop_id = prefix + str(int(random.random() * 100000))
        return prop_id

class Lot(models.Model):
    # land ownership
    # this lot relates to property listing X
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    # depending on shape, square_meters may not equal (width * depth)
    square_meters = models.FloatField()
    # measurement aligned to street-facing side of lot if possible
    width = models.FloatField()
    # measurement of how far back from street property extends
    depth = models.FloatField()
    description = models.TextField()
    zoning = models.CharField(max_length=100, default="residential")


class House(models.Model):
    # The primary residence that is for sale. May be a building on a lot, or a houseboat, or a mobile home.
    GARAGES = (
        ('0', 'No garage'),
        ('1', '1-car garage'),
        ('2', '2-car garage'),
        ('3', '2+ car garage')
    )
    # this house relates to property listing X
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    # year the building was constructed
    year = models.IntegerField()
    # rooms meant to be used as bedrooms
    beds = models.IntegerField()
    # toilet, sink, and tub or shower
    baths = models.IntegerField()
    # toilet, sink
    halfbaths = models.IntegerField()
    # floor space of all rooms together
    square_meters = models.FloatField()
    # floors or storeys. half-floors due to hills are ignored.
    floors = models.IntegerField()
    # basements, or floors below ground. User discretion.
    basements = models.IntegerField()
    # Any room you can drive a car into and close the door is a garage.
    # assumption: there's only 1 attached garage per house.
    garage = models.CharField(max_length=1, choices=GARAGES)
    # Parking situation (dedicated street parking, street, underground, garage, helipad...)
    parking = models.CharField(max_length=100)
    # catch-all for additional features such as alarm system, fireplace, pool, sauna, etc.
    extras = models.TextField()


class Suite(House):
    # Representing condos in a city, different details than a house such as unit number, and strata fees.
    # room unit 221A, 4, #209, 2211B, 2-1104
    unit_number = models.CharField(max_length=10)
    annual_strata_fee = models.FloatField()
    pet_rules = models.CharField(max_length=100)
    shared_fitness_room = models.BooleanField(default=False)
    shared_pool = models.BooleanField(default=False)
    shared_party_room = models.BooleanField(default=False)
    shared_private_courtyard = models.BooleanField(default=False)
    shared_laundry = models.BooleanField(default=False)
    units_in_building = models.IntegerField()
    building_floors = models.IntegerField()


class Structure(models.Model):
    # Structures other than the primary residence on the same lot. May already be leased out.
    # building is on or part of lot X
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    square_meters = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    height = models.FloatField()
    description = models.TextField()


class HouseRoom(models.Model):
    # describing rooms in the house
    # The room is in house X
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    square_meters = models.FloatField()
    # which floor is it on? (1 is ground -1 is basement. No 0.)
    floor = models.IntegerField()
    # bedroom, bathroom, kitchen, storage, multi-purpose, ...
    role = models.CharField(max_length=100)


class SuiteRoom(models.Model):
    # describing rooms in the suite
    # The room is in suite X
    suite = models.ForeignKey(Suite, on_delete=models.CASCADE)
    square_meters = models.FloatField()
    # which floor is it on? (1 is ground -1 is basement. No 0.)
    floor = models.IntegerField()
    # bedroom, bathroom, kitchen, storage, multi-purpose, ...
    role = models.CharField(max_length=100)






