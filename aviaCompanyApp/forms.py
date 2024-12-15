from django import forms
from . import models
from django.core.exceptions import ValidationError
import datetime
from django.db.models import F

class BookingStatusForm(forms.Form):
    surname = forms.CharField(widget=forms.TextInput(attrs={'class': 'сol-5 form-control', 'placeholder': 'Фамилия пассажира'}), label='')
    ticket_num = forms.CharField(widget=forms.TextInput(attrs={'class': 'сol-4 form-control', 'placeholder': 'Номер билета'}), label='')

class BuyTicketsForm(forms.Form):
    departure_city = forms.ModelChoiceField(queryset=models.Airport.objects.filter(status=models.Airport.STATUS_CHOICES[0][0]).values_list('nearest_city', flat=True).distinct(), 
                                            widget=forms.Select(attrs={'class': 'form-select index-left-forms'}), label='', empty_label='Откуда')
    arrival_city = forms.ModelChoiceField(queryset=models.Airport.objects.filter(status=models.Airport.STATUS_CHOICES[0][0]).values_list('nearest_city', flat=True).distinct(), 
                                          widget=forms.Select(attrs={'class': 'form-select index-middle-forms'}), label='', empty_label='Куда')
    flight_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control index-middle-forms', 
                                                                'type': 'date', 'value': datetime.date.today(),
                                                                'min': datetime.date.today() + datetime.timedelta(days=1),
                                                                'max': datetime.date.today() + datetime.timedelta(days=90)}), label='')

class LoginForm(forms.Form):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control mt-1 mb-2', 'placeholder': 'Почта'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Пароль'}, render_value=False))
    not_a_robot = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input ms-2 mb-3', 'id': 'login_not_a_robot'}))

    def clean(self):
        data = super().clean()
        if not data['not_a_robot']:
            raise ValidationError('Вы - робот?')
        return data

class RegisterForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control mt-1 mb-2', 'placeholder': 'Почта'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Надежный пароль'}, render_value=False))
    repeat_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Тот же самый надежный пароль'}, render_value=False))
    not_a_robot = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input ms-2 mb-3', 'id': 'register_not_a_robot'}))

    def clean(self):
        data = super().clean()
        if not data['password'] and not data['repeat_password']:
            raise ValidationError('Пароль не должен быть пустым!')
        if data['repeat_password'] != data['password']:
            raise ValidationError('Пароли не совпадают!')
        if models.CustomUser.objects.filter(email=data['email']).exists():
            raise ValidationError('Эта почта уже занята!')
        if not data['not_a_robot']:
            raise ValidationError('Вы - робот?')
        return data
        
class UpdateUserForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mt-1 mb-1'}), label='Фамилия', required=False)
    surname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-1'}), label='Имя', required=False)
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-1'}), label='Электронная почта', 
                            error_messages={'invalid': 'Некорректный адрес почты'})
    phone_num = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2'}), label='Номер телефона', required=False, 
                                validators=[models.phone_regex])

    class Meta:
        model = models.CustomUser
        fields = ['first_name', 'surname', 'email', 'phone_num']

class DocForm(forms.ModelForm):
    added_check = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'form-check-input ms-2 mb-3'}), label='Добавлен', required=False)
    custom_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-1'}))
    type = forms.ChoiceField(choices=models.Doc.TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-select mb-1'}), label='Тип документа')
    number = forms.CharField(max_length=10, min_length=10, required=True, widget=forms.TextInput(attrs={'class': 'form-control mb-1'}), label='Серия и номер документа')
    date_of_issue = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 
                                                                'min': datetime.date.today() + datetime.timedelta(weeks=-3650),
                                                                'max': datetime.date.today()}, format=('%Y-%m-%d')), label='Дата выдачи')
    class Meta:
        model = models.Doc
        fields = ['added_check', 'custom_name', 'type', 'date_of_issue', 'number']

