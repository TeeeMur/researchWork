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
    buyTicketsForm = BuyTicketsForm()
    return render(request, 'index.html', {'bookingForm': bookingForm,
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
def user_docs(request):
    docsForms = []
    docs = list(Doc.objects.filter(owner=request.user))
    if docs:
        for i in range(len(docs)):
            docsForms.append(DocForm(instance=docs[i], initial={'added_check': True}))
    if len(docs) != 10:
        docsForms.append(DocForm())
    if request.method == "POST":
        url_next = request.GET.get('next')
        doc_num = -1
        prev_custom_name = None
        for i in range(len(docs)):
            if docs[i].custom_name in request.POST:
                inputDocForm = DocForm(request.POST, instance=docs[i])
                doc_num=i
                prev_custom_name = docs[i].custom_name
                break
        else:
            inputDocForm = DocForm(request.POST)
        if inputDocForm.is_valid():
            if prev_custom_name == None:
                if inputDocForm.cleaned_data['added_check'] == False:
                    docsForms[-1] = inputDocForm
                    messages.add_message(request=request, level=messages.WARNING, message='Если хотите сохранить документ, отметьте пункт \"Сохранить\"')
                    return render(request, 'profile_docs.html', {'docsForms': docsForms})
                else:
                    inputDoc = inputDocForm.save(commit=False)
                    inputDoc.owner = request.user
                    inputDoc.save()
                    if url_next:
                        return redirect(url_next)
                    messages.add_message(request=request, level=messages.INFO, message=f'Документ {inputDocForm.cleaned_data['custom_name']} был успешно добавлен')
                    docsForms[-1] = DocForm(instance=inputDoc, initial={'added_check': True})
                    if len(docsForms) != 10:
                        docsForms.append(DocForm())
            else:
                if inputDocForm.cleaned_data['added_check'] == False:
                    doc_to_delete = docs[doc_num]
                    docsForms.pop(doc_num)
                    if len(docsForms) == 9:
                        docsForms.append(DocForm())
                    doc_to_delete.delete()
                    messages.add_message(request=request, level=messages.INFO, message=f'Документ {inputDocForm.cleaned_data['custom_name']} был успешно удален')
                else:
                    inputDoc = inputDocForm.save(commit=False)
                    inputDoc.pk = docs[doc_num].pk
                    inputDoc.save()
                    messages.add_message(request=request, level=messages.INFO, message=f'Документ {inputDocForm.cleaned_data['custom_name']} был успешно изменен')
                    docsForms[doc_num] = DocForm(instance=inputDoc)
    return render(request, 'profile_docs.html', {'docsForms': docsForms})


def my_ticket(request):
    curr_ticket_slug = request.GET.get('curr_ticket_slug')
    curr_ticket = Ticket.objects.get(ticket_slug=curr_ticket_slug)
    services_for_flight = Service.objects.get_services_for_flight_by_ticket(curr_ticket)
    if not curr_ticket.flightseat and curr_ticket.flight.status == 'EXP':
        can_choose_seat = Service.objects.get(name='Выбор места') in set(services_for_flight).intersection(set(curr_ticket.services.all()))
        if can_choose_seat:
            if request.method == 'POST':
                chooseSeatForm = ChooseSeatForm(request.POST)
                if chooseSeatForm.is_valid():
                    flightseat = chooseSeatForm.seat_number
                    curr_ticket.flightseat = flightseat
                    curr_ticket.save()
        else:
            if request.method == 'POST':
                request_params = request.POST
    return render(request, 'ticket_booking.html', {'curr_ticket': curr_ticket, 'services_for_flight': services_for_flight, 
                                                   'choose_seat_form': chooseSeatForm})

def search_ticket(request):
    ticket_surname = request.GET.get('surname')
    ticket_slug = request.GET.get('ticket_num')
    ticket = Ticket.objects.get(slugField=ticket_slug, client__surname=ticket_surname)
    return redirect(reverse('my_ticket', curr_ticket=ticket))


@login_required
def profile_tickets(request):
    curr_profile = request.user
    profile_tickets = Ticket.objects.filter(client=curr_profile).all().order_by('-flight__date_departure', '-flight__time_departure')
    return render(request, 'profile_tickets.html', {'profile_tickets': profile_tickets})


@login_required
def ticket_preview(request, flight_slug, add_lug):
    curr_flight = Flight.objects.get(slugField=flight_slug)
    available_services = Service.objects.get_services_for_flight(curr_flight)
    client_docs = Doc.objects.filter(owner=request.user).all()
    if request.method == 'POST':
        request_params = request.POST
        

    return render(request, 'buy_ticket_menu.html', {'curr_flight': curr_flight, 'add_lug': add_lug, 'available_services': available_services, 
                                                    'client_docs': client_docs})

@login_required
def curr_ticket_preview(request, flight_slug, add_lug):
    curr_flight = Flight.objects.get(slugField=flight_slug)
    available_services = Service.objects.get_services_for_flight(curr_flight)
    client_docs = Doc.objects.filter(owner=request.user).all()
    if request.method == 'POST':
        params = request.POST
        print(params)
        print('A;KDFJA;SLDFJKAS;LDJFSD;LFJK;LJK;FLDAJK;FLAKDSJ')
        print(params['client_doc'])
        curr_doc = Doc.objects.get(owner=request.user, custom_name=params['client_doc'])
        new_ticket = Ticket(client=request.user, cart=Cart.objects.get(client=request.user), flight=curr_flight, price=curr_flight.price, document=curr_doc)
        new_ticket.save()
        for each_service_name in params.getlist('services'):
            new_ticket.services.add(Service.objects.get(name=each_service_name))
    return render(request, 'buy_ticket_menu_copy.html', {'curr_flight': curr_flight, 'add_lug': add_lug, 'available_services': available_services, 
                                                    'client_docs': client_docs})
