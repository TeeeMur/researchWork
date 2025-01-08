from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.urls import reverse
from django.contrib import auth, messages
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import random
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
                    if url_next:
                        return redirect(url_next)
                    messages.add_message(request=request, level=messages.INFO, message=f'Документ {inputDocForm.cleaned_data['custom_name']} был успешно изменен')
                    docsForms[doc_num] = DocForm(instance=inputDoc, initial={'added_check': True})
    return render(request, 'profile_docs.html', {'docsForms': docsForms})


def my_ticket(request, curr_ticket_slug):
    curr_ticket = Ticket.objects.get(ticket_slug=curr_ticket_slug)
    services_for_flight = Service.objects.get_services_for_flight_by_ticket(curr_ticket)
    can_choose_seat = Service.objects.get(name="Выбор места") in services_for_flight.filter(in_ticket=True)
    chooseSeatForm = ChooseSeatForm(flight=curr_ticket.flight)
    if request.method == 'POST':
        available_seats = FlightSeat.objects.get_available_seats(curr_flight=curr_ticket.flight)
        if request.POST.get('seat_number'):
            chosen_seat = available_seats.get(seat_num=request.POST.get('seat_number'))
            chosen_seat.ticket_num = curr_ticket
            chosen_seat.save()
        else:
            chosen_seat = random.choice(available_seats)
            chosen_seat.save()
    return render(request, 'bought_ticket_view.html', {'curr_ticket': curr_ticket, 'services_for_flight': services_for_flight, 
                                                       'can_choose_seat': can_choose_seat,
                                                       'choose_seat_form': chooseSeatForm})

def current_bought_ticket(request):
    ticket_surname = request.GET.get('surname')
    ticket_slug = request.GET.get('ticket_num')
    ticket = Ticket.objects.get(ticket_slug=ticket_slug, document__surname=ticket_surname)
    return redirect(reverse('my_ticket', kwargs={'curr_ticket_slug':ticket.ticket_slug}))

@login_required
def profile_tickets(request):
    curr_profile = request.user
    profile_tickets = Ticket.objects.get_profile_purchased_tickets(curr_profile)
    return render(request, 'profile_tickets.html', {'profile_tickets': profile_tickets})

@login_required
def curr_ticket_preview(request, flight_slug, add_lug):
    curr_flight = Flight.objects.get(slugField=flight_slug)
    available_services = Service.objects.get_services_for_flight(curr_flight)
    client_docs = Doc.objects.filter(owner=request.user).all()
    if request.method == 'POST':
        params = request.POST
        if 'client_doc' not in params:
            messages.warning(request, "К билету необходимо прикрепить документ!")
            return render(request, 'ticket_config.html', {'curr_flight': curr_flight, 'add_lug': add_lug, 'available_services': available_services, 
                                                    'client_docs': client_docs})
        curr_doc = Doc.objects.filter(owner=request.user, custom_name=params['client_doc']).first()
        new_ticket = Ticket(client=request.user, cart=Cart.objects.get(client=request.user), flight=curr_flight, price=curr_flight.price, document=curr_doc)
        new_ticket.save()
        for each_service_name in params.getlist('services'):
            add_service = Service.objects.get(name=each_service_name)
            new_ticket.services.add(add_service)
            new_ticket.price += add_service.price
        new_ticket.save()
        if 'to_cart' in params:
            return redirect(reverse('cart'))
    return render(request, 'ticket_config.html', {'curr_flight': curr_flight, 'add_lug': add_lug, 'available_services': available_services, 
                                                    'client_docs': client_docs})

@login_required
def cart(request):
    curr_cart_tickets = Ticket.objects.get_tickets_in_cart(client=request.user)
    cart_sum = curr_cart_tickets.aggregate(models.Sum('price'))['price__sum']
    if request.method == "POST":
        docs_counter = False
        last_tickets = Ticket.objects.count_last_tickets_cart(client=request.user)
        tickets_count_map = dict()
        tickets_list = list(curr_cart_tickets)
        for each_ticket in tickets_list:
            flight = each_ticket.flight
            if flight in tickets_count_map:
                tickets_count_map[flight] += 1
            else:
                tickets_count_map[flight] = 1
            docs_count = Doc.objects.filter(models.Q(ticket__flight=flight) & models.Q(id=each_ticket.document.id)).count()
            docs_counter = docs_count > 1 or docs_counter
        for each_flight in list(tickets_count_map.keys()):
            flight_last_tickets = last_tickets.filter(flight=each_flight).count()
            if flight_last_tickets >= tickets_count_map[each_flight]:
                tickets_count_map.pop(each_flight)
        if len(tickets_count_map) != 0:
            flights_string = ", ".join(list(tickets_count_map.keys()))
            messages.warning(request, "На рейсы " + flights_string + " недостаточно билетов.")
        if docs_counter:
            messages.warning(request, 'На один документ оформлено несколько билетов!')
        if len(messages.get_messages(request)) == 0:
            curr_cart_tickets.update(purchased=True, cart=None)
            return redirect(reverse('profile.tickets'))
    return render(request, 'cart.html', {'cart_tickets': curr_cart_tickets, 'cart_sum': cart_sum})

@login_required
def ticket_config_from_cart(request, ticket_slug):
    curr_ticket = Ticket.objects.get(cart=request.user.cart, ticket_slug=ticket_slug)
    client_docs = Doc.objects.filter(owner=request.user).all()
    available_services = Service.objects.get_services_for_flight_by_ticket(curr_ticket)
    if request.method == 'POST':
        chosen_doc = Doc.objects.get(owner=request.user, custom_name=request.POST['client_doc'])
        curr_ticket.document = chosen_doc
        curr_ticket.save()
    return render(request, 'ticket_config_in_cart.html', {'curr_ticket': curr_ticket, 'available_services': available_services, 
                                                    'client_docs': client_docs})

@require_POST
def edit_service_in_cart(request, ticket_slug, service_id):
    curr_ticket = Ticket.objects.get(ticket_slug=ticket_slug)
    curr_service = Service.objects.get(pk=service_id)
    response = ''
    if (curr_service in curr_ticket.services.all()):
        curr_ticket.services.remove(curr_service)
        curr_ticket.price -= curr_service.price
        curr_ticket.save()
        response = 'REMOVED'
    else:
        curr_ticket.services.add(curr_service)
        curr_ticket.price += curr_service.price
        curr_ticket.save()
        response = 'ADDED'
    return JsonResponse({'response': response, 'ticket_price': curr_ticket.price, 'service_name': curr_service.name, 'service_price': curr_service.price})

@require_POST
def edit_service_bought(request, ticket_slug, service_id):
    curr_ticket = Ticket.objects.get(ticket_slug=ticket_slug)
    curr_service = Service.objects.get(pk=service_id)
    curr_ticket.services.add(curr_service)
    curr_ticket.price += curr_service.price
    curr_ticket.save()
    return JsonResponse({'service_name': curr_service.name, 'service_price': curr_service.price})



def remove_ticket(request, ticket_slug):
    curr_ticket = Ticket.objects.get(ticket_slug=ticket_slug)
    curr_ticket.delete()
    return redirect(reverse('cart'))