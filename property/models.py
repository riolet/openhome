from django.core.exceptions import ValidationError
from django.db import models
import re


class User(models.Model):
    #Any contact information needed to let buyer reach seller. Minimum is email.
    login_email = models.CharField("Login", max_length=100, null=False, blank=False, primary_key=True)
    email = models.CharField("Email address", max_length=100, null=False, blank=True)
    phone = models.CharField("Phone number", max_length=100, null=False, blank=True)
    fax = models.CharField("Fax number", max_length=100, null=False, blank=True)
    mail = models.CharField("Mailing address", max_length=200, null=False, blank=True)
    message = models.TextField(null=False, blank=True)
    b_email = models.BooleanField("Show email", default=True)
    b_phone = models.BooleanField("Show phone number", default=False)
    b_fax = models.BooleanField("Show fax", default=False)
    b_mail = models.BooleanField("Show mailing address", default=False)
    last_login = models.DateTimeField("Last Login", null=False)

    def __str__(self):
        return self.login_email


#  Property validators:
def validate_postal_code(value):
    # Note: Can switch on country to switch formatting styles
    if not re.match(r'^[A-Z]\d[A-Z]\d[A-Z]\d$', value):
        raise ValidationError("Postal Code doesn't match A1A 1A1 format")


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

    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    creation_stamp = models.DateTimeField('creation time')
    publish_stamp = models.DateTimeField('publish time', null=True, blank=True, default=None)
    edit_stamp = models.DateTimeField('latest edit time')
    status = models.CharField(max_length=1, choices=STATUS)
    description = models.TextField()
    price = models.FloatField()
    property_tax = models.FloatField()
    property_type = models.CharField(max_length=50)

    # Location information
    country = models.CharField(max_length=3, choices=COUNTRIES)
    province = models.CharField(max_length=2, choices=PROVINCES)
    region = models.CharField(max_length=100, null=False, blank=True)
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100, null=False, blank=True)
    street_address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=6, null=False, blank=False, validators=[validate_postal_code])
    # lat/long at 6 decimal places = 1.113m precision.
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=False, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=False, blank=True)

    def normalize_fields(self):
        """
        Trim spaces and newlines, convert to numbers, and capitalize as needed.

        user-submitted data in fields:
            status
            description
            price
            property_tax
            property_type
            country
            province
            region
            city
            neighborhood
            street_address
            postal_code
            latitude
            longitude
        """
        self.status = self.status.upper().strip()
        self.description = self.description.strip()
        self.price = float(self.price)
        self.property_tax = float(self.property_tax)
        self.property_type = self.property_type.strip()
        self.country = self.country.upper().strip()
        self.province = self.province.upper().strip()
        self.region = self.region.strip()
        self.city = self.city.strip()
        self.neighborhood = self.neighborhood.strip()
        self.street_address = self.street_address.strip()
        self.postal_code = self.postal_code.replace(' ', '').strip()
        self.latitude = ((float(self.latitude) + 180) % 360) - 180
        self.longitude = ((float(self.longitude) + 180) % 360) - 180

    def escape_fields(self):
        """
        Django's ORM automatically escapes data being inserted into it.
        Django's template engine automatically escapes html being inserted into elements.
        Any additional escaping should be done here.

        user-submitted data in fields:
            status
            description
            price
            property_tax
            property_type
            country
            province
            region
            city
            neighborhood
            street_address
            postal_code
            latitude
            longitude
        """
        pass

    def generate_id(self):
        p_code = str(self.postal_code)
        d_stamp = str(int(self.creation_stamp.timestamp() // 86400))  # 86400 is seconds/day
        prefix = p_code + d_stamp
        try:
            latest = Property.objects.filter(id__startswith=prefix).order_by('-id')[0]
            # increment the last 9 symbols. modulus 1e9.
            next_num = int(latest.id[11:]) + 1
            next_num = int(next_num % 1e9)
        except IndexError:
            next_num = 1
        prop_id = "{}{:09d}".format(prefix, next_num)
        return prop_id

    def __str__(self):
        return self.id


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

    def __str__(self):
        return "{}sqm in {}".format(self.square_meters, self.property)


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

    def __str__(self):
        return "{}-bed, {}-storey house".format(self.beds, self.floors)


class Suite(models.Model):
    # Representing condos in a city, different details than a house such as unit number, and strata fees.
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

    def __str__(self):
        return "{}-bed, {}-sqm suite".format(self.beds, self.square_meters)


class Structure(models.Model):
    # Structures other than the primary residence on the same lot. May already be leased out.
    # building is on or part of lot X
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    square_meters = models.FloatField()
    width = models.FloatField()
    depth = models.FloatField()
    height = models.FloatField()
    description = models.TextField()

    def __str__(self):
        return "{:.3g}x{:.3g}x{:.3g} structure".format(self.width, self.depth, self.height)


class HouseRoom(models.Model):
    # describing rooms in the house
    # The room is in house X
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    square_meters = models.FloatField()
    # which floor is it on? (1 is ground -1 is basement. No 0.)
    floor = models.IntegerField()
    # bedroom, bathroom, kitchen, storage, multi-purpose, ...
    role = models.CharField(max_length=100)

    def __str__(self):
        return "{}sqm {}".format(self.square_meters, self.role[:20])


class SuiteRoom(models.Model):
    # describing rooms in the suite
    # The room is in suite X
    suite = models.ForeignKey(Suite, on_delete=models.CASCADE)
    square_meters = models.FloatField()
    # which floor is it on? (1 is ground -1 is basement. No 0.)
    floor = models.IntegerField()
    # bedroom, bathroom, kitchen, storage, multi-purpose, ...
    role = models.CharField(max_length=100)

    def __str__(self):
        return "{}sqm {}".format(self.square_meters, self.role[:20])






