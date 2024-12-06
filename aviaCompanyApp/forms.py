from django import forms
from . import models

class BookingStatusForm(forms.Form):
    surname = forms.CharField(widget=forms.TextInput(attrs={'class': 'сol-5 form-control', 'placeholder': 'Фамилия пассажира'}), label='')
    ticket_num = forms.CharField(widget=forms.TextInput(attrs={'class': 'сol-4 form-control', 'placeholder': 'Номер билета'}), label='')

class TicketRegisterForm(forms.Form):
    surname = forms.CharField(widget=forms.TextInput(attrs={'class': 'сol-5 form-control', 'placeholder': 'Фамилия пассажира'}), label='')
    ticket_num = forms.CharField(widget=forms.TextInput(attrs={'class': 'сol-4 form-control', 'placeholder': 'Номер билета'}), label='')

class BuyTicketsForm(forms.Form):
    departure_city = forms.ModelChoiceField(queryset=models.Airport.objects.all(), widget=forms.Select(attrs={'class': 'form-select index-left-forms'}), label='', empty_label='Откуда')
    arrival_city = forms.ModelChoiceField(queryset=models.Airport.objects.all(), widget=forms.Select(attrs={'class': 'form-select index-middle-forms'}), label='', empty_label='Куда')
    flight_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control index-middle-forms', 'type': 'date'}), label='')