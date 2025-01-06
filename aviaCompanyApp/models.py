from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.core.exceptions import FieldError, ValidationError
from itertools import product
from datetime import datetime, timedelta, time
from django.template.defaultfilters import slugify

phone_regex = RegexValidator(regex=r'^\+?\d{9,15}$', message='Некорректный номер телефона')
airport_code_validator = RegexValidator(regex=r'^[A-Z][A-Z][A-Z][A-Z]?$')


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save()
        Cart.objects.create(client=user)
        return user
    
    def create_user(self, email, password, first_name, surname, phone_num):
            if not email:
                raise ValueError("The Email must be set")
            email = self.normalize_email(email)
            user = self.model(email=email, first_name=first_name, surname=surname, phone_num=phone_num)
            user.set_password(password)
            user.save()
            Cart.objects.create(client=user)
            return user
    

    def create_superuser(self, email, password):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=True, is_superuser=True)
        user.set_password(password)
        user.save()
        Cart.objects.create(client=user)
        return user
    
class FlightManager(models.Manager):
    def get_flight_by_cities_and_date_ordtime(self, dep_city, dest_city, date):
        time_dep_border = time(hour=0, minute=0)
        if str(datetime.now().date()) == str(date) and datetime.now().hour >= 21:
            time_dep_border = time(hour=23, minute=59)
        elif str(datetime.now().date()) == str(date):
            time_dep_border = datetime.now() + timedelta(hours=3)
        return self.select_related('airway').annotate(tickets_count=(models.F('airway__plane__load_capacity') - models.Count('ticket', filter=models.Q(ticket__purchased=True)))).filter(airway__departure_airport__nearest_city=dep_city, 
                                                               airway__destination_airport__nearest_city=dest_city, 
                                                               date_departure=date, tickets_count__gt=0, 
                                                               time_departure__gt=time_dep_border, status='PLD').order_by('time_arrival')
    
class ServicesManager(models.Manager):
    def get_services_for_flight(self, flight):
        return self.filter(airway=flight.airway).all()
    def get_services_for_flight_by_ticket(self, ticket):
        ticket_services = ticket.services.all()
        return self.filter(airway=ticket.flight.airway).all().annotate(in_ticket=models.Case(models.When(id__in=ticket_services, then=True), default=False, output_field=models.BooleanField()))
    
class TicketManager(models.Manager):
    def get_tickets_in_cart(self, client):
        return self.filter(cart__client=client).order_by('flight','-created_at').all()
    def count_last_tickets_cart(self, client):
        return self.filter(cart__client=client) \
            .annotate(tickets_count=(models.F('flight__airway__plane__load_capacity') - models.Count('purchased', filter=models.Q(purchased=True)))) \
            .values('flight', 'tickets_count')
    def get_profile_purchased_tickets(self, client):
        return self.filter(client=client, purchased=True).all().order_by('-flight__date_departure', '-flight__time_departure').all()

class CustomUser(AbstractBaseUser, PermissionsMixin):
    MAX_DOCS = 2
    first_name = models.CharField(max_length=43, null=True, blank=True)
    surname = models.CharField(max_length=43, null=True, blank=True)
    email = models.EmailField(unique=True, blank=False)
    phone_num = models.CharField(validators=[phone_regex], null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    objects = CustomUserManager()

class Doc(models.Model):
    TYPE_CHOICES = (
        ('PSP', 'Паспорт'),
        ('BRT', 'Свидетельство о рождении'),
        ('IPS', 'Заграничный паспорт'), 
    )
    type = models.CharField(choices=TYPE_CHOICES)
    custom_name = models.CharField(max_length=40)
    first_name = models.CharField(max_length=43)
    surname = models.CharField(max_length=43)
    number = models.CharField(validators=[RegexValidator(regex=r'^\d{10}$')])
    date_of_issue = models.DateField()
    owner = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['number', 'type', 'date_of_issue', 'custom_name'], ['custom_name', 'owner']]
    

class Pilot(models.Model): 
    first_name = models.CharField(max_length=43)
    surname = models.CharField(max_length=43)
    middle_name = models.CharField(max_length=43, null=True, blank=True)
    experience = models.IntegerField()
    phone_num = models.CharField(validators=[phone_regex])

    def __str__(self):
        return f'{self.surname} {self.first_name} {self.middle_name}'

class Staff(models.Model):
    first_name = models.CharField(max_length=43)
    surname = models.CharField(max_length=43)
    middle_name = models.CharField(max_length=43, null=True, blank=True)
    phone_num = models.CharField(validators=[phone_regex])
    position = models.CharField()

    def __str__(self):
        return f'{self.surname} {self.first_name} {self.middle_name}'

class Airport(models.Model):

    STATUS_CHOICES = (
        ('WR', 'Работает'),
        ('TN', 'Временно не работает'), 
        ('CL', 'Закрыт')
    )
    nearest_city = models.CharField()
    name = models.CharField(max_length=50)
    international_code = models.CharField(validators=[airport_code_validator], primary_key=True)
    status = models.CharField(choices=STATUS_CHOICES)

    def __str__(self):
        return self.name


class Service(models.Model):
    SERVICES_TYPES = (
        ('LS', 'Услуги по багажу'),
        ('FFS', 'Услуги питания'),
        ('ODF', 'Другие услуги во время полета'),
        ('OAF', 'Другие услуги до/после полета'),
    )
    type = models.CharField(choices=SERVICES_TYPES)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField()

    objects = ServicesManager()

    def __str__(self):
        return f'{self.name}'
    

class PassengerPlane(models.Model):
    STATUS_CHOICES = (
        ('UR', 'В ремонте'),
        ('ACT', 'В работе'),
    )
    on_board_number = models.CharField(primary_key=True, validators=[RegexValidator(regex=r'^[A-Z][A-Z]-\d{4,5}$')])
    manufacturer = models.CharField(max_length=60)
    model = models.CharField(max_length=60)
    load_capacity = models.IntegerField()
    max_flight_range = models.IntegerField()
    service_life = models.IntegerField()
    status = models.CharField(choices=STATUS_CHOICES)

    def __str__(self):
        return f'{self.on_board_number} {self.manufacturer} {self.model}'

class Airway(models.Model):
    STATUS_CHOICES = (
        ('CMP', 'Активный'),
        ('IDT', 'В разработке'),
        ('CLS', 'Закрыт')
    )
    number = models.CharField(primary_key=True)
    departure_airport = models.ForeignKey(to=Airport, on_delete=models.SET_NULL, 
                                          null=True, related_name='%(class)s_dep_Airport')
    destination_airport = models.ForeignKey(to=Airport, on_delete=models.SET_NULL, 
                                            null=True, related_name='%(class)s_dest_Airport')
    departure_time = models.TimeField()
    flight_duration = models.DurationField()
    pilots = models.ManyToManyField(to=Pilot)
    staff = models.ManyToManyField(to=Staff)
    services = models.ManyToManyField(to=Service)
    plane = models.ForeignKey(to=PassengerPlane, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.number} {self.departure_airport.nearest_city}-{self.destination_airport.nearest_city}'
    
    def flight_duration_hhmm(self):
        seconds_value = self.flight_duration.total_seconds()
        hours = int(seconds_value // 3600)
        minutes = int(seconds_value % 3600 // 60)
        return f'{hours}ч {minutes}мин'


class Weekday(models.Model):
    WEEK_DAYS = (
        ('MON', 'Понедельник'),
        ('TUE', 'Вторник'),
        ('WED', 'Среда'),
        ('THU', 'Четверг'),
        ('FRI', 'Пятница'),
        ('SAT', 'Суббота'),
        ('SUN', 'Воскресенье'),
    )
    day = models.CharField(choices=WEEK_DAYS)
    airway = models.ForeignKey(to=Airway, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.get_day_display()}: {self.airway}'


class Flight(models.Model):
    STATUS_CHOICES = (
        ('PLD', 'Запланирован'),
        ('EXP','Ожидается'),
        ('PRP', 'В подготовке'),
        ('IFL','В полете'),
        ('CTD','Выполнен'),
        ('CLD','Отменен'),
        ('DLD','Задерживается'),
    )
    slugField = models.SlugField(unique=True, db_index=True)
    airway = models.ForeignKey(to=Airway, on_delete=models.PROTECT)
    date_departure = models.DateField()
    time_departure = models.TimeField(blank=True, null=True)
    date_arrival = models.DateField(blank=True, null=True)
    time_arrival = models.TimeField(blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES)
    price = models.IntegerField()

    objects = FlightManager()

    def extra_lug_price(self):
        extra_lug_name = 'Дополнительный багаж'
        if Service.objects.filter(name=extra_lug_name).first() is None:
            return LookupError(f'Услуга \"{extra_lug_name}\" не найдена')
        return self.price + Service.objects.filter(name='Дополнительный багаж').first().price
    
    def __str__(self):
        return f'{self.airway.number}{self.date_departure}'
    
    def save(self, *args, **kwargs):
        approved_weekdays = list(Weekday.objects.filter(airway=self.airway).values_list('day', flat=True))
        if str(Weekday.WEEK_DAYS[self.date_departure.isoweekday() - 1]) not in approved_weekdays:
            raise ValidationError('Дата и день недели не совпадают')
        if self.time_departure is None:
            self.time_departure = self.airway.departure_time
        if not self.slugField:
            self.slugField = slugify((self.airway.number + str(self.date_departure)))
        if self.date_arrival is None and self.time_arrival is None:
            arrival_datetime = datetime.combine(self.date_departure, self.airway.departure_time) + self.airway.flight_duration
            self.date_arrival = arrival_datetime.date()
            self.time_arrival = arrival_datetime.time()
        super(Flight, self).save(*args, **kwargs)
        if FlightSeat.objects.filter(flight=self).first() is None:
            seats_count = self.airway.plane.load_capacity
            seats = list(map(lambda x: FlightSeat(seat_num="".join(x), flight=self), product([str(i) for i in range(seats_count//6 + 1)], 'ABCDEF')))[0:seats_count]
            FlightSeat.objects.bulk_create(seats)
        return self

class Cart(models.Model):
    client = models.OneToOneField(to=CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.client)

class Ticket(models.Model):
    ticket_slug = models.SlugField(unique=True, db_index=True)
    client = models.ForeignKey(to=CustomUser, on_delete=models.DO_NOTHING)
    cart = models.ForeignKey(to=Cart, on_delete=models.PROTECT, null=True, blank=True)
    flight = models.ForeignKey(to=Flight, on_delete=models.PROTECT)
    services = models.ManyToManyField(Service)
    price = models.IntegerField()
    document = models.ForeignKey(to=Doc, on_delete=models.PROTECT)
    purchased = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.ticket_slug}'
    
    def save(self, *args, **kwargs):
        flight_tickets = Ticket.objects.filter(client=self.client, flight=self.flight)
        if not self.ticket_slug:
            self.ticket_slug = slugify(str(self.flight) + str(self.client.email.split('@')[0]) + str(flight_tickets.count()))
        return super(Ticket, self).save(*args, **kwargs)
    
    objects = TicketManager()
    
class FlightSeat(models.Model):
    flight = models.ForeignKey(to=Flight, on_delete=models.CASCADE)
    seat_num = models.CharField(validators=[RegexValidator(r'^\d\d?[A-F]$')])
    ticket_num=models.OneToOneField(to=Ticket, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        if self.ticket_num != None and self.ticket_num.flight != self.flight:
            return ValidationError('Место и билет должны относиться к одному полету!')
        return super().clean()

    def __str__(self):
        return f'{self.flight} {self.seat_num}'
    