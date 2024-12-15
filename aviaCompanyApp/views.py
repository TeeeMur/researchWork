from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.urls import reverse
from django.contrib import auth, messages
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

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

@login_required
def ticket_view(request, flight_slug, add_lug):
    curr_flight = Flight.objects.get(slugField=flight_slug)
    available_services = Service.objects.get_services_for_flight(curr_flight)
    client_docs = Doc.objects.filter(owner=request.user).all()
    if request.method == 'POST':
        doc = None
        services = set()
        price_sum = curr_flight.price
        curr_ticket = Ticket(flight=curr_flight, client=request.user)
        for each in request.POST:
            if each in client_docs.values_list('custom_name', flat=True):
                doc = Doc.objects.filter(owner=request.user, custom_name=each).first()
            elif each in available_services.values_list('name', flat=True):
                service = Service.objects.get(name=each)
                price_sum += service.price
                services.add(service)
        if doc == None:
            messages.add_message(request=request, message='Прикрепите, пожалуйста, документ', level=messages.WARNING)
            return render(request, 'buy_ticket_menu.html', {'curr_flight': curr_flight, 'add_lug': add_lug, 'available_services': available_services, 
                                                    'client_docs': client_docs})
        curr_ticket.document = doc
        curr_ticket.booking_status = 'NO'
        curr_ticket.price = price_sum
        print(price_sum)
        curr_ticket.save()
        for service in services:
            curr_ticket.services.add(service)
        return render(request, 'ticket_booking.html', {'curr_ticket': curr_ticket})
    return render(request, 'buy_ticket_menu.html', {'curr_flight': curr_flight, 'add_lug': add_lug, 'available_services': available_services, 
                                                    'client_docs': client_docs})

def login(request):
    loginForm = LoginForm()
    if request.method == 'POST':
        loginForm = LoginForm(request.POST)
        if loginForm.is_valid():
            user = auth.authenticate(request, **loginForm.cleaned_data)
            if user:
                auth.login(request, user)
                next_page = request.GET.get('next')
                if next_page:
                    url = next_page
                else:
                    url = reverse('index')
                return redirect(url)
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
        url_next = request.GET.get('next')
        doc_num = -1
        prev_custom_name = None
        if len(docs) == 1 and docs[0].custom_name in request.POST:
            inputDocForm = DocForm(request.POST, instance=docs[0])
            doc_num = 0
            prev_custom_name = docs[0].custom_name
        elif len(docs) > 1 and docs[1].custom_name in request.POST:
            inputDocForm = DocForm(request.POST, instance=docs[1])
            doc_num = 1
            prev_custom_name = docs[1].custom_name
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
                if url_next:
                    return redirect(url_next)
                return render(request, 'profile_docs.html', {'docsForms': docsForms})
            elif inputDocForm.cleaned_data['added_check'] == False:
                docsForms[0] = inputDocForm
                messages.add_message(request=request, level=messages.WARNING, message='Если хотите сохранить документ, отметьте пункт \"Добавлен\"')
                messages.add_message(request=request, level=messages.WARNING, message='Для удаления cохраненного документа оставьте пустым пункт \"Добавлен\"')
                return render(request, 'profile_docs.html', {'docsForms': docsForms})
            inputDoc = inputDocForm.save(commit=False)
            if prev_custom_name is not None:
                moved_doc_pk = Doc.objects.get(owner=request.user, custom_name=prev_custom_name).pk
                inputDoc.id = moved_doc_pk  
            inputDoc.owner = request.user
            inputDoc.save()
            docsForms = [DocForm(), DocForm()]
            docs = list(Doc.objects.filter(owner=request.user))
            for i in range(len(docs)):
                docsForms[i] = DocForm(instance=docs[i], initial={'added_check': True})
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            messages.add_message(request=request, level=messages.INFO, message='Документы были успешно изменены')
            if url_next:
                    return redirect(url_next)
            return render(request, 'profile_docs.html', {'docsForms': docsForms})
    return render(request, 'profile_docs.html', {'docsForms': docsForms})


def my_ticket(request):
    curr_ticket = request.GET.get('curr_ticket')
    services_for_flight = Flight.objects.get_services_for_flight(curr_ticket.flight)
    return render(request, 'ticket_booking.html', {'curr_ticket': curr_ticket})

def search_ticket(request):
    ticket_surname = request.GET.get('surname')
    ticket_slug = request.GET.get('ticket_num')
    ticket = Ticket.objects.get(slugField=ticket_slug, client__surname=ticket_surname)
    return redirect(reverse('my_ticket', curr_ticket=ticket))


@login_required
def profile_tickets(request):
    curr_profile = request.user
    profile_tickets = Ticket.objects.filter(client=curr_profile).all()
    return render(request, 'profile_tickets.html', {'profile_tickets':profile_tickets})