from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
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
        self.status = self.status.upper().strip()[:1]
        self.description = self.description.strip()
        self.price = float(self.price)
        self.property_tax = float(self.property_tax)
        self.property_type = self.property_type.strip()
        self.country = self.country.upper().strip()[:3]
        self.province = self.province.upper().strip()[:2]
        self.region = self.region.strip()
        self.city = self.city.strip()
        self.neighborhood = self.neighborhood.strip()
        self.street_address = self.street_address.strip()
        self.postal_code = self.postal_code.replace(' ', '').strip()
        self.latitude = ((float(self.latitude) + 180) % 360) - 180
        self.longitude = ((float(self.longitude) + 180) % 360) - 180

    def update(self, params):
        if 'status' in params:
            self.status = params['status']
        if 'description' in params:
            self.description = params['description']
        if 'price' in params:
            self.price = params['price']
        if 'property_tax' in params:
            self.property_tax = params['property_tax']
        if 'property_type' in params:
            self.property_type = params['property_type']
        if 'country' in params:
            self.country = params['country']
        if 'province' in params:
            self.province = params['province']
        if 'region' in params:
            self.region = params['region']
        if 'city' in params:
            self.city = params['city']
        if 'neighborhood' in params:
            self.neighborhood = params['neighborhood']
        if 'street_address' in params:
            self.street_address = params['street_address']
        if 'postal_code' in params:
            self.postal_code = params['postal_code']
        if 'latitude' in params:
            self.latitude = params['latitude']
        if 'longitude' in params:
            self.longitude = params['longitude']

    def export(self):
        data = {
            'status': self.status,
            'description': self.description,
            'price': self.price,
            'property_tax': self.property_tax,
            'property_type': self.property_type,
            'country': self.country,
            'province': self.province,
            'region': self.region,
            'city': self.city,
            'neighborhood': self.neighborhood,
            'street_address': self.street_address,
            'postal_code': self.postal_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }
        return data

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

    @staticmethod
    def construct_default(owner):
        p = Property()
        p.owner = owner
        p.creation_stamp = timezone.now()
        p.publish_stamp = None
        p.edit_stamp = timezone.now()
        p.status = 'U'
        p.description = 'blank property listing'
        p.price = 1
        p.property_type = 'unspecified'
        p.property_tax = 1
        p.country = 'CAN'
        p.province = 'BC'
        p.region = ''
        p.city = 'unspecified'
        p.neighborhood = ''
        p.street_address = 'unspecified'
        p.postal_code = 'A1A1A1'
        p.latitude = 1.0
        p.longitude = 1.0
        return p

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
    zoning = models.CharField(max_length=100, default="residential")
    description = models.TextField()

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
        self.square_meters = float(self.square_meters)
        self.width = float(self.width)
        self.depth = float(self.depth)
        self.zoning = self.zoning.strip()
        self.description = self.description.strip()

    def update(self, params):
        if 'square_meters' in params:
            self.square_meters = params['square_meters']
        if 'width' in params:
            self.width = params['width']
        if 'depth' in params:
            self.depth = params['depth']
        if 'zoning' in params:
            self.zoning = params['zoning']
        if 'description' in params:
            self.description = params['description']

    def export(self):
        data = {
            'square_meters': self.square_meters,
            'width': self.width,
            'depth': self.depth,
            'zoning': self.zoning,
            'description': self.description
        }
        return data

    @staticmethod
    def construct_default(property):
        l = Lot()
        l.property = property
        l.square_meters = 4
        l.width = 2
        l.depth = 2
        l.description = 'blank'
        l.zoning = 'residential'
        return l

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
    extras = models.TextField(null=False, blank=True)

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
        self.year = int(self.year)
        self.beds = int(self.beds)
        self.baths = int(self.baths)
        self.halfbaths = int(self.halfbaths)
        self.square_meters = float(self.square_meters)
        self.floors = int(self.floors)
        self.basements = int(self.basements)
        self.garage = self.garage.strip()[:1]
        self.parking = self.parking.strip()
        self.extras = self.extras.strip()

    def update(self, params):
        if 'year' in params:
            self.year = params['year']
        if 'beds' in params:
            self.beds = params['beds']
        if 'baths' in params:
            self.baths = params['baths']
        if 'halfbaths' in params:
            self.halfbaths = params['halfbaths']
        if 'square_meters' in params:
            self.square_meters = params['square_meters']
        if 'floors' in params:
            self.floors = params['floors']
        if 'basements' in params:
            self.basements = params['basements']
        if 'garage' in params:
            self.garage = params['garage']
        if 'parking' in params:
            self.parking = params['parking']
        if 'extras' in params:
            self.extras = params['extras']

    def export(self):
        data = {
            'year': self.year,
            'beds': self.beds,
            'baths': self.baths,
            'halfbaths': self.halfbaths,
            'square_meters': self.square_meters,
            'floors': self.floors,
            'basements': self.basements,
            'garage': self.garage,
            'parking': self.parking,
            'extras': self.extras,
        }
        return data

    @staticmethod
    def construct_default(property):
        h = House()
        h.property = property
        h.year = 2000
        h.beds = 0
        h.baths = 0
        h.halfbaths = 0
        h.square_meters = 0
        h.floors = 0
        h.basements = 0
        h.garage = '0'
        h.parking = "unspecified"
        h.extras = ""
        return h

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
    extras = models.TextField(null=False, blank=True)

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
        self.year = int(self.year)
        self.beds = int(self.beds)
        self.baths = int(self.baths)
        self.halfbaths = int(self.halfbaths)
        self.square_meters = float(self.square_meters)
        self.floors = int(self.floors)
        self.basements = int(self.basements)
        self.garage = self.garage.strip()[:1]
        self.parking = self.parking.strip()
        self.extras = self.extras.strip()
        self.unit_number = self.unit_number.strip()[:10]
        self.annual_strata_fee = float(self.annual_strata_fee)
        self.pet_rules = self.pet_rules.strip()[:100]
        self.shared_fitness_room = bool(self.shared_fitness_room)
        self.shared_pool = bool(self.shared_pool)
        self.shared_party_room = bool(self.shared_party_room)
        self.shared_private_courtyard = bool(self.shared_private_courtyard)
        self.shared_laundry = bool(self.shared_laundry)
        self.units_in_building = int(self.units_in_building)
        self.building_floors = int(self.building_floors)

    def update(self, params):
        if 'year' in params:
            self.year = params['year']
        if 'beds' in params:
            self.beds = params['beds']
        if 'baths' in params:
            self.baths = params['baths']
        if 'halfbaths' in params:
            self.halfbaths = params['halfbaths']
        if 'square_meters' in params:
            self.square_meters = params['square_meters']
        if 'floors' in params:
            self.floors = params['floors']
        if 'basements' in params:
            self.basements = params['basements']
        if 'garage' in params:
            self.garage = params['garage']
        if 'parking' in params:
            self.parking = params['parking']
        if 'extras' in params:
            self.extras = params['extras']
        if 'unit_number' in params:
            self.unit_number = params['unit_number']
        if 'annual_strata_fee' in params:
            self.annual_strata_fee = params['annual_strata_fee']
        if 'pet_rules' in params:
            self.pet_rules = params['pet_rules']
        if 'shared_fitness_room' in params:
            self.shared_fitness_room = params['shared_fitness_room']
        if 'shared_pool' in params:
            self.shared_pool = params['shared_pool']
        if 'shared_party_room' in params:
            self.shared_party_room = params['shared_party_room']
        if 'shared_private_courtyard' in params:
            self.shared_private_courtyard = params['shared_private_courtyard']
        if 'shared_laundry' in params:
            self.shared_laundry = params['shared_laundry']
        if 'units_in_building' in params:
            self.units_in_building = params['units_in_building']
        if 'building_floors' in params:
            self.building_floors = params['building_floors']

    def export(self):
        data = {
            'year': self.year,
            'beds': self.beds,
            'baths': self.baths,
            'halfbaths': self.halfbaths,
            'square_meters': self.square_meters,
            'floors': self.floors,
            'basements': self.basements,
            'garage': self.garage,
            'parking': self.parking,
            'extras': self.extras,
        }
        return data

    @staticmethod
    def construct_default(property):
        s = Suite()
        s.property = property
        s.year = 2000
        s.beds = 0
        s.baths = 0
        s.halfbaths = 0
        s.square_meters = 0
        s.floors = 0
        s.basements = 0
        s.garage = '0'
        s.parking = "unspecified"
        s.extras = ""
        s.unit_number = '0'
        s.annual_strata_fee = 0
        s.pet_rules = 'None'
        s.shared_fitness_room = False
        s.shared_laundry = False
        s.shared_party_room = False
        s.shared_pool = False
        s.shared_private_courtyard = False
        s.units_in_building = 0
        s.building_floors = 0
        return s

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
        self.square_meters = float(self.square_meters)
        self.width = float(self.width)
        self.depth = float(self.depth)
        self.height = float(self.height)
        self.description = self.description.strip()

    def update(self, params):
        if 'square_meters' in params:
            self.square_meters = params['square_meters']
        if 'width' in params:
            self.width = params['width']
        if 'depth' in params:
            self.depth = params['depth']
        if 'height' in params:
            self.height = params['height']
        if 'description' in params:
            self.description = params['description']

    def export(self):
        data = {
            'square_meters': self.square_meters,
            'width': self.width,
            'height': self.height,
            'depth': self.depth,
            'description': self.description
        }
        return data

    @staticmethod
    def construct_default(lot):
        s = Structure()
        s.lot = lot
        s.square_meters = 0
        s.width = 0
        s.depth = 0
        s.height = 0
        s.description = 'unspecified structure'
        return s

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
        self.square_meters = float(self.square_meters)
        self.floor = int(self.floor)
        self.role = self.role.strip()[:100]

    def update(self, params):
        print("update params: {}".format(params))
        if 'square_meters' in params:
            self.square_meters = params['square_meters']
        if 'floor' in params:
            self.floor = params['floor']
        if 'role' in params:
            self.role = params['role']

    def export(self):
        data = {
            'square_meters': self.square_meters,
            'floor': self.floor,
            'role': self.role,
        }
        return data

    @staticmethod
    def construct_default(house):
        r = HouseRoom()
        r.house = house
        r.square_meters = 0
        r.floor = 1
        r.role = "unspecified"
        return r

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
        self.square_meters = float(self.square_meters)
        self.floor = int(self.floor)
        self.role = self.role.strip()[:100]

    def update(self, params):
        if 'square_meters' in params:
            self.square_meters = params['square_meters']
        if 'floor' in params:
            self.floor = params['floor']
        if 'role' in params:
            self.role = params['role']

    def export(self):
        data = {
            'square_meters': self.square_meters,
            'floor': self.floor,
            'role': self.role,
        }
        return data

    @staticmethod
    def construct_default(suite):
        r = SuiteRoom()
        r.suite = suite
        r.square_meters = 0
        r.floor = 1
        r.role = "unspecified"
        return r

    def __str__(self):
        return "{}sqm {}".format(self.square_meters, self.role[:20])
