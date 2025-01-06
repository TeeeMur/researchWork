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
    path('profile/docs/', views.user_docs, name='profile.docs'),
    path('logout/', views.logout, name='logout'),
    path('ticket_view/<slug:flight_slug>/<int:add_lug>/', views.curr_ticket_preview, name='ticket_view'),
    path('ticket_view_from_cart/<slug:ticket_slug>/', views.ticket_config_from_cart, name='ticket_config_cart'),
    path('my_ticket/', views.my_ticket, name='my_ticket'),
    path('personal_tickets/', views.profile_tickets, name='profile.tickets'),
    path('search_ticket/', views.current_bought_ticket, name='bought_ticket'),
    path('cart/', views.cart, name='cart'),
    path('ticket_view_from_cart/<slug:ticket_slug>/async_edit_service_cart/<int:service_id>/', views.edit_service_in_cart, name='edit_service_in_cart'),
    path('ticket_remove/<slug:ticket_slug>/', views.remove_ticket, name='ticket_remove')
]
