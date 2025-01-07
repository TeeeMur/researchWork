from django.contrib import admin
from .models import *

class AirwayAdmin(admin.ModelAdmin):
    search_fields = ['number', 'departure_airport__nearest_city', 
                     'destination_airport__nearest_city', 'weekday']
    
class FlightAdmin(admin.ModelAdmin):
    search_fields = ['slugField', 'airway', 
                     'date_departure', 'date_arrival', 'status']
    
class CartAdmin(admin.ModelAdmin):
    search_fields = ['client__email', 'flight', 
                     'flight__airway']
    
class PasssengerPlaneAdmin(admin.ModelAdmin):
    search_fields = ['manufacturer', 'model', 
                     'load_capacity', 'service_life']

class TicketInline(admin.TabularInline):
    model = FlightSeat

class TicketAdmin(admin.ModelAdmin):
    inlines = [TicketInline,]

admin.site.register(CustomUser)
admin.site.register(Airway, AirwayAdmin)
admin.site.register(Airport)
admin.site.register(Cart)
admin.site.register(Doc)
admin.site.register(Pilot)
admin.site.register(Service)
admin.site.register(Staff)
admin.site.register(Flight)
admin.site.register(FlightSeat)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(PassengerPlane)
admin.site.register(Weekday)
