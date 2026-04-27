from django.urls import path
from . import views

urlpatterns = [
    # Patient booking
    path('book/',                          views.doctor_list,         name='doctor_list'),
    path('book/<uuid:doctor_id>/',         views.book_slots,          name='book_slots'),
    path('appointments/',                  views.my_appointments,     name='my_appointments'),
    path('appointments/<int:pk>/cancel/',  views.cancel_appointment,  name='cancel_appointment'),

    # Doctor
    path('doctor/appointments/',                      views.pending_appointments, name='pending_appointments'),
    path('doctor/appointments/<int:pk>/approve/',     views.approve_appointment,  name='approve_appointment'),
    path('doctor/appointments/<int:pk>/decline/',     views.decline_appointment,  name='decline_appointment'),
    path('doctor/schedule/',                          views.manage_schedule,      name='manage_schedule'),
]
