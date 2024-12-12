from django.shortcuts import render, redirect
from .forms import *
from .models import CustomUser
from django.urls import reverse
from django.contrib import auth, messages
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseServerError

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
    print(request_params)
    return render(request, 'flight_search_results.html')

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
    docs = list(models.Doc.objects.filter(owner=request.user))
    for i in range(len(docs)):
        docsForms[i] = DocForm(instance=docs[i], initial={'added_check': True})
    if request.method == "POST":
        doc_num = -1
        if len(docs) == 1 and docs[0].custom_name in request.POST:
            inputDocForm = DocForm(request.POST, instance=docs[0])
        elif len(docs) > 1 and docs[1].custom_name in request.POST:
            inputDocForm = DocForm(request.POST, instance=docs[1])
            doc_num = 1
        else:
            inputDocForm = DocForm(request.POST)
        if inputDocForm.is_valid():
            if inputDocForm.cleaned_data['added_check'] == False and doc_num > -1:
                docs[doc_num].delete()
                docsForms = [DocForm(), DocForm()]
                docs = list(models.Doc.objects.filter(owner=request.user))
                for i in range(len(docs)):
                    docsForms[i] = DocForm(instance=docs[i], initial={'added_check': True})
                return render(request, 'profile_docs.html', {'docsForms': docsForms})
            inputDoc = inputDocForm.save(commit=False)
            inputDoc.owner = request.user
            inputDoc.save()
            docsForms = [DocForm(), DocForm()]
            docs = list(models.Doc.objects.filter(owner=request.user))
            for i in range(len(docs)):
                docsForms[i] = DocForm(instance=docs[i], initial={'added_check': True})
            return render(request, 'profile_docs.html', {'docsForms': docsForms})
        else:
            print(inputDocForm.errors)
    return render(request, 'profile_docs.html', {'docsForms': docsForms})

