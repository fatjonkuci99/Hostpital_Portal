from django.urls import path
from . import views

urlpatterns = [
    path('',              views.home_page,        name='home'),
    path('login/',        views.login_page,       name='login'),
    path('staff/login/',  views.staff_login_page, name='staff_login'),
    path('logout/',       views.logout_page,      name='logout'),
    path('dashboard/',    views.dashboard_router,  name='dashboard'),
]
