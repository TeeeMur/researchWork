from django.shortcuts import render
from . import forms

# Create your views here.


def index(request):
    bookingForm = forms.BookingStatusForm()
    ticketRegisterForm = forms.TicketRegisterForm()
    buyTicketsForm = forms.BuyTicketsForm()
    return render(request, 'index.html', {'bookingForm': bookingForm,
                                          'ticketRegisterForm': ticketRegisterForm,
                                          'buyTicketsForm': buyTicketsForm})
