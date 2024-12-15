from django.core.management.base import BaseCommand, CommandParser
from aviaCompanyApp.models import *
from faker import Faker
import random, datetime
class Command(BaseCommand):
    def handle(self, *args, **options):
        faker = Faker('ru_RU')
        staff_male_positions=['Техник', 'Стюард']
        airports = [
            Airport(nearest_city='Новосибирск', name='Толмачёво', international_code='OVB', status='WR'),
            Airport(nearest_city='Казань', name='Казань', international_code='KZN', status='WR'),
            Airport(nearest_city='Санкт-Петербург', name='Пулково', international_code='LED', status='WR'),
            Airport(nearest_city='Москва', name='Шереметьево', international_code='SVO', status='WR'),
            Airport(nearest_city='Москва', name='Внуково', international_code='VKO', status='WR'),
            Airport(nearest_city='Сочи', name='Сочи', international_code='AER', status='WR'),
            Airport(nearest_city='Екатеринбург', name='Кольцово', international_code='SVX', status='WR'),
        ]
        Airport.objects.bulk_create(airports)

        planes = [
            PassengerPlane(on_board_number='RA-1777', manufacturer='Boeing', model='777', load_capacity=272, max_flight_range=10000, service_life=2, status='ACT'),
            PassengerPlane(on_board_number='RA-1350', manufacturer='Airbus', model='A350', load_capacity=210, max_flight_range=11000, service_life=3, status='ACT'),
            PassengerPlane(on_board_number='RA-2350', manufacturer='Airbus', model='A350', load_capacity=210, max_flight_range=11000, service_life=2, status='ACT'),
            PassengerPlane(on_board_number='RA-1320', manufacturer='Airbus', model='A320', load_capacity=162, max_flight_range=9500, service_life=6, status='ACT'),
            PassengerPlane(on_board_number='RA-1787', manufacturer='Boeing', model='787', load_capacity=195, max_flight_range=12000, service_life=3, status='ACT'),
            PassengerPlane(on_board_number='RA-2787', manufacturer='Boeing', model='787', load_capacity=264, max_flight_range=12000, service_life=3, status='ACT'),
            PassengerPlane(on_board_number='RA-1747', manufacturer='Boeing', model='747', load_capacity=324, max_flight_range=9800, service_life=9, status='ACT'),
            PassengerPlane(on_board_number='RA-1737', manufacturer='Boeing', model='737 MAX', load_capacity=228, max_flight_range=9800, service_life=10, status='ACT'),
            PassengerPlane(on_board_number='RA-2737', manufacturer='Boeing', model='737 MAX', load_capacity=228, max_flight_range=9800, service_life=10, status='ACT'),
        ]
        PassengerPlane.objects.bulk_create(planes)

        pilots = [
            Pilot(first_name=faker.first_name_male(), surname=faker.last_name_male(), middle_name=faker.middle_name_male(), experience=random.randint(1,50), phone_num=faker.msisdn()[:10])
            for i in range(60)
        ]
        pilots.extend([
            Pilot(first_name=faker.first_name_female(), surname=faker.last_name_female(), middle_name=faker.middle_name_female(), experience=random.randint(1,50), phone_num=faker.msisdn()[:10])
            for i in range(30)
        ])
        Pilot.objects.bulk_create(pilots)

        staff = [
            Staff(first_name=faker.first_name_female(), surname=faker.last_name_female(), middle_name=faker.middle_name_female(), position='Стюардесса', phone_num=faker.msisdn()[:10])
            for i in range(50)
        ]
        staff.extend([
            Staff(first_name=faker.first_name_male(), surname=faker.last_name_male(), middle_name=faker.middle_name_male(), position=random.choice(staff_male_positions), phone_num=faker.msisdn()[:10])
            for i in range(50)
        ])
        Staff.objects.bulk_create(staff)

        services = [
            Service(type='LS', name='Дополнительный багаж', description='Возможность взять с собой в поездку помимо ручной клади багаж весом не более 23 кг.', 
                    price=1000),
            Service(type='FFS', name='Дополнительный легкий перекус', 
                    description='Дополнительный набор, в состав которого входит сытный бутерброд и напиток на выбор: вода, кофе или сок.', 
                    price=600),
            Service(type='LS', name='Перевозка спортивного инвентаря', description='Возможность взять с собой в поездку спортивный инвентарь, ' +
                    'выходящий за нормативные размеры дополнительного багажа.', price=800),
            Service(type='OAF', name='Выбор места', description='Возможность самостоятельно выбрать место в самолете.', price=800),
        ]
        Service.objects.bulk_create(services)

        users = [
            CustomUser(first_name=faker.first_name_female(), surname=faker.last_name_female(), email=f'{i}_{faker.safe_email()}', phone_num=faker.msisdn()[:10], 
                       password=faker.msisdn()[:10])
            for i in range(300)
        ]
        users.extend([
            CustomUser(first_name=faker.first_name_male(), surname=faker.last_name_male(), email=f'{i}_{faker.safe_email()}', phone_num=faker.msisdn()[:10], 
                       password=faker.msisdn()[:10])
            for i in range(300)
        ])
        CustomUser.objects.bulk_create(users)
        users_for_docs = list(CustomUser.objects.all())
        docs = [
            Doc(type='PSP', custom_name=f'{i + 1}_doc', date_of_issue=datetime.date(2010, 4, 10) + datetime.timedelta(weeks=i), 
                number=faker.msisdn()[:10], owner=users_for_docs[i]) for i in range(600)
        ]
        Doc.objects.bulk_create(docs)
        airways = [
            Airway(number='KZSVO', departure_airport=Airport.objects.get(pk='KZN'), destination_airport=Airport.objects.get(pk='SVO'), 
                   departure_time=datetime.time(hour=11, minute=20), flight_duration=datetime.timedelta(minutes=100), plane=PassengerPlane.objects.get(pk='RA-1737')),

            Airway(number='SVOKZ', departure_airport=Airport.objects.get(pk='SVO'), destination_airport=Airport.objects.get(pk='KZN'), 
                   departure_time=datetime.time(hour=19, minute=30), flight_duration=datetime.timedelta(minutes=100), plane=PassengerPlane.objects.get(pk='RA-1737')),

            Airway(number='VKOVB', departure_airport=Airport.objects.get(pk='VKO'), destination_airport=Airport.objects.get(pk='OVB'), 
                   departure_time=datetime.time(hour=9, minute=15), flight_duration=datetime.timedelta(minutes=250), plane=PassengerPlane.objects.get(pk='RA-1350')),

            Airway(number='OVBVK', departure_airport=Airport.objects.get(pk='OVB'), destination_airport=Airport.objects.get(pk='VKO'), 
                   departure_time=datetime.time(hour=18, minute=5), flight_duration=datetime.timedelta(minutes=250), plane=PassengerPlane.objects.get(pk='RA-1350')),

            Airway(number='LEDAER', departure_airport=Airport.objects.get(pk='LED'), destination_airport=Airport.objects.get(pk='AER'), 
                   departure_time=datetime.time(hour=8, minute=25), flight_duration=datetime.timedelta(minutes=200), plane=PassengerPlane.objects.get(pk='RA-1787')),

            Airway(number='AERLED', departure_airport=Airport.objects.get(pk='AER'), destination_airport=Airport.objects.get(pk='LED'), 
                   departure_time=datetime.time(hour=16, minute=20), flight_duration=datetime.timedelta(minutes=200), plane=PassengerPlane.objects.get(pk='RA-1787')),

            Airway(number='VKSVX', departure_airport=Airport.objects.get(pk='VKO'), destination_airport=Airport.objects.get(pk='SVX'), 
                   departure_time=datetime.time(hour=6, minute=35), flight_duration=datetime.timedelta(minutes=150), plane=PassengerPlane.objects.get(pk='RA-2737')),

            Airway(number='SVXVK', departure_airport=Airport.objects.get(pk='SVX'), destination_airport=Airport.objects.get(pk='VKO'), 
                   departure_time=datetime.time(hour=18, minute=20), flight_duration=datetime.timedelta(minutes=150), plane=PassengerPlane.objects.get(pk='RA-2737')),

            Airway(number='SVXKZ', departure_airport=Airport.objects.get(pk='SVX'), destination_airport=Airport.objects.get(pk='KZN'), 
                   departure_time=datetime.time(hour=11, minute=20), flight_duration=datetime.timedelta(minutes=105), plane=PassengerPlane.objects.get(pk='RA-1320')),

            Airway(number='KZSVX', departure_airport=Airport.objects.get(pk='KZN'), destination_airport=Airport.objects.get(pk='SVX'), 
                   departure_time=datetime.time(hour=11, minute=20), flight_duration=datetime.timedelta(minutes=105), plane=PassengerPlane.objects.get(pk='RA-1320')),

            Airway(number='KZSVO1', departure_airport=Airport.objects.get(pk='KZN'), destination_airport=Airport.objects.get(pk='SVO'), 
                   departure_time=datetime.time(hour=17, minute=35), flight_duration=datetime.timedelta(minutes=100), plane=PassengerPlane.objects.get(pk='RA-2787')),

            Airway(number='SVOKZ1', departure_airport=Airport.objects.get(pk='SVO'), destination_airport=Airport.objects.get(pk='KZN'), 
                   departure_time=datetime.time(hour=8, minute=45), flight_duration=datetime.timedelta(minutes=100), plane=PassengerPlane.objects.get(pk='RA-2787')),
                   
            Airway(number='LEDOVB', departure_airport=Airport.objects.get(pk='LED'), destination_airport=Airport.objects.get(pk='OVB'), 
                   departure_time=datetime.time(hour=6, minute=40), flight_duration=datetime.timedelta(minutes=280), plane=PassengerPlane.objects.get(pk='RA-2350')),

            Airway(number='OVBLED', departure_airport=Airport.objects.get(pk='OVB'), destination_airport=Airport.objects.get(pk='LED'), 
                   departure_time=datetime.time(hour=18, minute=50), flight_duration=datetime.timedelta(minutes=280), plane=PassengerPlane.objects.get(pk='RA-2350')),
        ]
        Airway.objects.bulk_create(airways)
        airways_for_further_creates = list(Airway.objects.all())
        pilots_for_airways=list(Pilot.objects.all())
        staff_for_airways=list(Staff.objects.all())
        service_for_airways=list(Service.objects.all())
        for each_airway_index in range(len(airways_for_further_creates)):
            airways_for_further_creates[each_airway_index].pilots.add(pilots_for_airways[each_airway_index * 2], pilots_for_airways[each_airway_index * 2 + 1])
            airways_for_further_creates[each_airway_index].staff.add(staff_for_airways[each_airway_index * 3], 
                                                                       staff_for_airways[each_airway_index * 3 + 1], staff_for_airways[each_airway_index * 3 + 2])
            airways_for_further_creates[each_airway_index].services.add(*service_for_airways)

        weekdays = [
            Weekday(day=weekday, airway=airway) for weekday in Weekday.WEEK_DAYS for airway in airways_for_further_creates
        ]
        Weekday.objects.bulk_create(weekdays)
        dates_for_flights = [datetime.date(year=2024, month=12, day=(18 + i)) for i in range(10)]
        flights = [
            Flight(airway=airway, date_departure=flight_date, status='PLD', price=(2000 + airway.flight_duration.total_seconds() // 60 * 24)) 
            for airway in airways_for_further_creates for flight_date in dates_for_flights
        ]
        for each in flights:
            each.save()

