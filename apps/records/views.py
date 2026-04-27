import json
from datetime import datetime, timedelta, date

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from apps.accounts.models import User
from apps.accounts.utils import get_user_from_cookie
from .models import Appointment, DoctorSchedule, BlockedSlot


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _require_patient(request):
    user = get_user_from_cookie(request)
    if not user or user.role != User.PATIENT:
        return None, redirect('login')
    return user, None


def _require_doctor(request):
    user = get_user_from_cookie(request)
    if not user or user.role != User.DOCTOR:
        return None, redirect('login')
    return user, None


def _get_available_slots(doctor, selected_date):
    weekday = selected_date.weekday()
    try:
        schedule = DoctorSchedule.objects.get(doctor=doctor, weekday=weekday, is_active=True)
    except DoctorSchedule.DoesNotExist:
        return [], None

    slot_duration = timedelta(minutes=schedule.slot_duration)
    start_dt = datetime.combine(selected_date, schedule.start_time)
    end_dt   = datetime.combine(selected_date, schedule.end_time)

    all_slots = []
    current = start_dt
    while current + slot_duration <= end_dt:
        all_slots.append(current)
        current += slot_duration

    booked = set(
        Appointment.objects.filter(
            doctor=doctor,
            date_time__date=selected_date,
            status__in=[Appointment.PENDING, Appointment.CONFIRMED],
        ).values_list('date_time', flat=True)
    )

    blocked = set(
        BlockedSlot.objects.filter(
            doctor=doctor,
            date_time__date=selected_date,
        ).values_list('date_time', flat=True)
    )

    now = timezone.now().replace(tzinfo=None)
    available = [s for s in all_slots if s not in booked and s not in blocked and s > now]
    return available, schedule


# ─── Patient: browse doctors ───────────────────────────────────────────────────

def doctor_list(request):
    user, err = _require_patient(request)
    if err:
        return err

    doctors = User.objects.filter(role=User.DOCTOR).prefetch_related('schedules')
    doctor_data = []
    for doctor in doctors:
        schedules = doctor.schedules.filter(is_active=True)
        specialty = schedules.first().specialty if schedules.exists() else ''
        available_days = [s.get_weekday_display() for s in schedules]
        doctor_data.append({
            'doctor':         doctor,
            'specialty':      specialty,
            'available_days': available_days,
        })

    return render(request, 'booking/doctors.html', {
        'user':        user,
        'doctor_data': doctor_data,
    })


# ─── Patient: pick a slot ─────────────────────────────────────────────────────

def book_slots(request, doctor_id):
    user, err = _require_patient(request)
    if err:
        return err

    doctor = get_object_or_404(User, pk=doctor_id, role=User.DOCTOR)
    schedules = DoctorSchedule.objects.filter(doctor=doctor, is_active=True)
    specialty = schedules.first().specialty if schedules.exists() else ''

    # Python weekday (0=Mon) → JS getDay (0=Sun): (day + 1) % 7
    available_weekdays_js = json.dumps(
        [(s.weekday + 1) % 7 for s in schedules]
    )

    selected_date   = None
    available_slots = []
    error           = None

    date_str = request.GET.get('date') or request.POST.get('date')
    if date_str:
        try:
            selected_date = date.fromisoformat(date_str)
            if selected_date < date.today():
                error = 'Please select a future date.'
            else:
                available_slots, _ = _get_available_slots(doctor, selected_date)
                if not available_slots and not error:
                    error = 'No available slots on this day.'
        except ValueError:
            error = 'Invalid date.'

    if request.method == 'POST' and 'slot' in request.POST and not error:
        slot_str = request.POST.get('slot')
        reason   = request.POST.get('reason', '').strip()
        try:
            slot_dt = datetime.fromisoformat(slot_str)
            already_booked = Appointment.objects.filter(
                doctor=doctor,
                date_time=slot_dt,
                status__in=[Appointment.PENDING, Appointment.CONFIRMED],
            ).exists()
            is_blocked = BlockedSlot.objects.filter(doctor=doctor, date_time=slot_dt).exists()

            if already_booked or is_blocked:
                error = 'That slot is no longer available. Please choose another.'
            else:
                Appointment.objects.create(
                    patient=user,
                    doctor=doctor,
                    date_time=slot_dt,
                    reason=reason or 'Not specified',
                    status=Appointment.PENDING,
                )
                return redirect('my_appointments')
        except ValueError:
            error = 'Invalid slot.'

    return render(request, 'booking/slots.html', {
        'user':                  user,
        'doctor':                doctor,
        'specialty':             specialty,
        'selected_date':         selected_date,
        'available_slots':       available_slots,
        'available_weekdays_js': available_weekdays_js,
        'today':                 date.today().isoformat(),
        'error':                 error,
    })


# ─── Patient: my appointments ─────────────────────────────────────────────────

def my_appointments(request):
    user, err = _require_patient(request)
    if err:
        return err

    appointments = Appointment.objects.filter(patient=user).select_related('doctor')
    return render(request, 'booking/my_appointments.html', {
        'user':         user,
        'appointments': appointments,
    })


def cancel_appointment(request, pk):
    user, err = _require_patient(request)
    if err:
        return err

    appointment = get_object_or_404(Appointment, pk=pk, patient=user)
    if appointment.status in [Appointment.PENDING, Appointment.CONFIRMED]:
        appointment.status = Appointment.CANCELLED
        appointment.save()
    return redirect('my_appointments')


# ─── Doctor: approve / decline ────────────────────────────────────────────────

def pending_appointments(request):
    user, err = _require_doctor(request)
    if err:
        return err

    pending  = Appointment.objects.filter(doctor=user, status=Appointment.PENDING).select_related('patient')
    upcoming = Appointment.objects.filter(doctor=user, status=Appointment.CONFIRMED).select_related('patient')

    return render(request, 'booking/doctor_appointments.html', {
        'user':     user,
        'pending':  pending,
        'upcoming': upcoming,
    })


def approve_appointment(request, pk):
    user, err = _require_doctor(request)
    if err:
        return err

    appointment = get_object_or_404(Appointment, pk=pk, doctor=user, status=Appointment.PENDING)
    appointment.status = Appointment.CONFIRMED
    appointment.save()
    return redirect('pending_appointments')


def decline_appointment(request, pk):
    user, err = _require_doctor(request)
    if err:
        return err

    appointment = get_object_or_404(Appointment, pk=pk, doctor=user, status=Appointment.PENDING)
    appointment.status = Appointment.CANCELLED
    appointment.save()
    return redirect('pending_appointments')


# ─── Doctor: manage schedule / block slots ────────────────────────────────────

def manage_schedule(request):
    user, err = _require_doctor(request)
    if err:
        return err

    schedules = DoctorSchedule.objects.filter(doctor=user, is_active=True)
    available_weekdays_js = json.dumps(
        [(s.weekday + 1) % 7 for s in schedules]
    )

    selected_date = None
    all_slots     = []
    error         = None

    date_str = request.GET.get('date') or request.POST.get('date')
    if date_str:
        try:
            selected_date = date.fromisoformat(date_str)
            weekday = selected_date.weekday()
            try:
                schedule = DoctorSchedule.objects.get(doctor=user, weekday=weekday, is_active=True)
                slot_duration = timedelta(minutes=schedule.slot_duration)
                start_dt = datetime.combine(selected_date, schedule.start_time)
                end_dt   = datetime.combine(selected_date, schedule.end_time)

                blocked_times = set(
                    BlockedSlot.objects.filter(
                        doctor=user, date_time__date=selected_date
                    ).values_list('date_time', flat=True)
                )
                booked_times = set(
                    Appointment.objects.filter(
                        doctor=user,
                        date_time__date=selected_date,
                        status__in=[Appointment.PENDING, Appointment.CONFIRMED],
                    ).values_list('date_time', flat=True)
                )

                current = start_dt
                while current + slot_duration <= end_dt:
                    all_slots.append({
                        'dt':      current,
                        'blocked': current in blocked_times,
                        'booked':  current in booked_times,
                    })
                    current += slot_duration

            except DoctorSchedule.DoesNotExist:
                error = 'You have no schedule set for this day.'
        except ValueError:
            error = 'Invalid date.'

    if request.method == 'POST' and 'slot' in request.POST and not error:
        slot_str = request.POST.get('slot')
        reason   = request.POST.get('reason', '').strip()
        try:
            slot_dt = datetime.fromisoformat(slot_str)
            blocked, created = BlockedSlot.objects.get_or_create(
                doctor=user, date_time=slot_dt,
                defaults={'reason': reason},
            )
            if not created:
                # Already blocked — unblock it
                blocked.delete()
        except ValueError:
            pass
        return redirect(f'/doctor/schedule/?date={date_str}')

    return render(request, 'booking/doctor_schedule.html', {
        'user':                  user,
        'selected_date':         selected_date,
        'all_slots':             all_slots,
        'available_weekdays_js': available_weekdays_js,
        'today':                 date.today().isoformat(),
        'error':                 error,
    })
