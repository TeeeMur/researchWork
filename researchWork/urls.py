"""
URL configuration for researchWork project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include

from aviaCompanyApp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ticket_search/', views.flight_search_results, name='index.ticket_search'),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/docs/', views.profile_docs, name='profile.docs'),
    path('logout/', views.logout, name='logout'),
    path('ticket_view/<slug:flight_slug>/<int:add_lug>/', views.ticket_view, name='ticket_view'),
    path('my_ticket/', views.my_ticket, name='my_ticket'),
    path('personal_tickets/', views.profile_tickets, name='profile.tickets'),
    path('search_ticket/', views.search_ticket, name='search_ticket'),
]
