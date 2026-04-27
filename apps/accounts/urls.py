from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='api-register'),
    path('login/',    views.login,    name='api-login'),
    path('logout/',   views.logout,   name='api-logout'),
    path('me/',       views.me,       name='api-me'),
]
