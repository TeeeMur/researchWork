from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Airway)
admin.site.register(Airport)
admin.site.register(Pilot)
admin.site.register(Service)
admin.site.register(Staff)
admin.site.register(Flight)
admin.site.register(FlightSeat)
admin.site.register(Ticket)
admin.site.register(PassengerPlane)
admin.site.register(Weekday)
