from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.urls import reverse
from django.contrib import auth, messages
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.decorators import login_required

# Create your views here.


def index(request):
    bookingForm = BookingStatusForm()
    ticketRegisterForm = TicketRegisterForm()
    buyTicketsForm = BuyTicketsForm()
    return render(request, 'index.html', {'bookingForm': bookingForm,
                                          'ticketRegisterForm': ticketRegisterForm,
                                          'buyTicketsForm': buyTicketsForm})

def flight_search_results(request):
    request_params = request.GET
    buyTicketsForm = BuyTicketsForm(request.GET)
    searchResults = Flight.objects.get_flight_by_cities_and_date_ordtime(dep_city=request_params['departure_city'],
                                                                 dest_city=request_params['arrival_city'],
                                                                 date=request_params['flight_date'])
    extra_lug = Service.objects.filter(name='Дополнительный багаж').first()
    return render(request, 'flights_search_results.html', {'flightSearchResults': searchResults, 'buyTicketsForm': buyTicketsForm, 
                                                           'extra_lug': extra_lug})

def ticket_view(request, flight_slug, add_lug):
    request_params = request.GET
    curr_flight = Flight.objects.get(slugField=flight_slug)
    return render(request, 'buy_ticket_menu.html', {'curr_flight': curr_flight})

def login(request):
    loginForm = LoginForm()
    if request.method == 'POST':
        loginForm = LoginForm(request.POST)
        if loginForm.is_valid():
            user = auth.authenticate(request, **loginForm.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect(reverse('index'))
            loginForm.add_error(field=NON_FIELD_ERRORS, error='Неправильный логин/пароль')
    return render(request, 'login.html', {'loginForm': loginForm})

@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))


def register(request):
    registerForm = RegisterForm() 
    if request.method == "POST":
        registerForm = RegisterForm(request.POST)
        if registerForm.is_valid():
            CustomUser.objects.create_user(email=registerForm.cleaned_data['email'], password=registerForm.cleaned_data['password'])
            user = auth.authenticate(request, username=registerForm.cleaned_data['email'], password=registerForm.cleaned_data['password'])
            if user:
                auth.login(request, user)
                return redirect(reverse('index'))
    return render(request, 'register.html', {'registerForm': registerForm})

@login_required
def profile(request):
    profileForm = UpdateUserForm(instance = request.user)
    if request.method == "POST":
        profileForm = UpdateUserForm(request.POST, instance=request.user)
        if profileForm.is_valid():
            profileForm.save()
            messages.success(request, 'Профиль успешно отредактирован')
            return render(request, 'profile.html', {'profileForm': profileForm})
    return render(request, 'profile.html', {'profileForm': profileForm})

@login_required
def profile_docs(request):
    docsForms = [DocForm(), DocForm()]
    docs = list(Doc.objects.filter(owner=request.user))
    for i in range(len(docs)):
        docsForms[i] = DocForm(instance=docs[i], initial={'added_check': True})
    if request.method == "POST":
        doc_num = -1
        if len(docs) == 1 and docs[0].custom_name in request.POST:
            inputDocForm = DocForm(request.POST, instance=docs[0])
            doc_num = 0
        elif len(docs) > 1 and docs[1].custom_name in request.POST:
            inputDocForm = DocForm(request.POST, instance=docs[1])
            doc_num = 1
        else:
            inputDocForm = DocForm(request.POST)
        if inputDocForm.is_valid():
            if inputDocForm.cleaned_data['added_check'] == False and doc_num > -1:
                docs[doc_num].delete()
                docsForms = [DocForm(), DocForm()]
                docs = list(Doc.objects.filter(owner=request.user))
                for i in range(len(docs)):
                    docsForms[i] = DocForm(instance=docs[i], initial={'added_check': True})
                messages.add_message(request=request, level=messages.INFO, message='Документы были успешно изменены')
                return render(request, 'profile_docs.html', {'docsForms': docsForms})
            elif inputDocForm.cleaned_data['added_check'] == False:
                docsForms[0] = inputDocForm
                messages.add_message(request=request, level=messages.WARNING, message='Если хотите сохранить документ, отметьте пункт \"Добавлен\"')
                messages.add_message(request=request, level=messages.WARNING, message='Для удаления cохраненного документа оставьте пустым пункт \"Добавлен\"')
                return render(request, 'profile_docs.html', {'docsForms': docsForms})
            inputDoc = inputDocForm.save(commit=False)
            inputDoc.owner = request.user
            inputDoc.save()
            docsForms = [DocForm(), DocForm()]
            docs = list(Doc.objects.filter(owner=request.user))
            for i in range(len(docs)):
                docsForms[i] = DocForm(instance=docs[i], initial={'added_check': True})
            messages.add_message(request=request, level=messages.INFO, message='Документы были успешно изменены')
            return render(request, 'profile_docs.html', {'docsForms': docsForms})
    return render(request, 'profile_docs.html', {'docsForms': docsForms})

