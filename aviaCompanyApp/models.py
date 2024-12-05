from django.db import models
from django.core.validators import RegexValidator

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')

class Client(models.Model):
    LOYALTY_CHOICES = {
        '1': 'Low loyalty program',
        '2': 'High loyalty program',
    }
    first_name = models.CharField(max_length=43)
    surname = models.CharField(max_length=43)
    middle_name = models.CharField(max_length=43)
    e_mail = models.EmailField()
    loyalty_program = models.CharField(choices=LOYALTY_CHOICES)
    phone_num = models.CharField(validators=[phone_regex])


class Pilot(models.Model): 
    first_name = models.CharField(max_length=43)
    surname = models.CharField(max_length=43)
    middle_name = models.CharField(max_length=43)
    experience = models.IntegerField()
    phone_num = models.CharField(validators=[phone_regex])

class Staff(models.Model):
    first_name = models.CharField(max_length=43)
    surname = models.CharField(max_length=43)
    middle_name = models.CharField(max_length=43)
    phone_num = models.CharField(validators=[phone_regex])
    position = models.CharField()

class Airport(models.Model):

    STATUS_CHOICES = {
        'WR': 'Working',
        'TN': 'Temporarily not working', 
        'CL': 'Closed'
    }
    nearest_city = models.CharField()
    status = models.CharField(choices=STATUS_CHOICES)
    max_wingspan = models.IntegerField()


class Service(models.Model):
    SERVICES_TYPES = {
        'PRS': 'Priority service',
        'LS': 'Luggage service',
        'FFS': 'Additional meal',
        'ODF': 'Other services during flight',
        'OAF': 'Other services after flight',
    }
    type = models.CharField(choices=SERVICES_TYPES)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    

class PassengerPlane(models.Model):
    STATUS_CHOICES = {
        'UR': 'Under repair',
        'ACT': 'Active',
    }
    id_number = models.CharField(primary_key=True)
    manufacturer = models.CharField(max_length=60)
    model = models.CharField(max_length=60)
    load_capacity = models.IntegerField()
    wingspan = models.IntegerField()
    max_flight_range = models.IntegerField()
    service_life = models.IntegerField()
    status = models.CharField(choices=STATUS_CHOICES)

    class Meta: 
        constraints = [
            models.CheckConstraint(
                name='plane_number_constraint',
                check=models.Q(id_number__contains='^[A-Z]{1,2}-[0-9]{5}$')
            )
        ]

class Weekday(models.Model):
    WEEK_DAYS = {
        'MON': 'Monday',
        'TUE': 'Tuesday',
        'WED': 'Wednesday',
        'THU': 'Thursday',
        'FRI': 'Friday',
        'SAT': 'Saturday',
        'SUN': 'Sunday',
    }
    day = models.CharField(primary_key=True, choices=WEEK_DAYS)

class Airway(models.Model):
    STATUS_CHOICES = {
        'CMP': 'Active',
        'IDT': 'In development',
        'CLS': 'Closed'
    }
    number = models.CharField(primary_key=True)
    departure_airport = models.ForeignKey(to=Airport, on_delete=models.SET_NULL, 
                                          null=True, related_name='%(class)s_dep_Airport')
    destination_airport = models.ForeignKey(to=Airport, on_delete=models.SET_NULL, 
                                            null=True, related_name='%(class)s_dest_Airport')
    departure_time = models.TimeField()
    flight_duration = models.IntegerField()
    pilots = models.ManyToManyField(to=Pilot)
    staff = models.ManyToManyField(to=Staff)
    services = models.ManyToManyField(to=Service)
    plane = models.ForeignKey(to=PassengerPlane, on_delete=models.SET_NULL, null=True)
    days_of_week = models.ManyToManyField(Weekday)


class Flight(models.Model):
    STATUS_CHOICES = {
        'CLD': 'Cancelled',
        'EXP': 'Expected',
        'DLD': 'Delayed',
        'IFL': 'In flight',
        'CTD': 'Completed',
    }
    airway = models.ForeignKey(to=Airway, on_delete=models.DO_NOTHING)
    date_departure = models.DateField()
    time_departure = models.TimeField()
    date_arrival = models.DateField()
    time_arrival = models.TimeField()
    status = models.CharField(choices=STATUS_CHOICES)

class Ticket(models.Model):
    STATUS_CHOICES = {
        'NO': 'Not booked',
        'YES': 'Booked'
    }
    client = models.ForeignKey(to=Client, on_delete=models.DO_NOTHING)
    flight = models.ForeignKey(to=Flight, on_delete=models.RESTRICT)
    seat_num = models.CharField(null=True)
    booking_status = models.CharField(choices=STATUS_CHOICES)
    services = models.ManyToManyField(Service)

    class Meta: 
        models.CheckConstraint(
                name="seat_num_constraint",
                condition=models.Q(seat_num__contains="^\d{1,2}\s{1}$")
            )