from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Appointment

COUNTED_STATUSES = {'completed', 'no_show'}


@receiver(pre_save, sender=Appointment)
def capture_old_status(sender, instance, **kwargs):
    """Store the current DB status on the instance before saving."""
    if instance.pk:
        try:
            instance._old_status = Appointment.objects.get(pk=instance.pk).status
        except Appointment.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Appointment)
def update_patient_no_show_stats(sender, instance, **kwargs):
    """
    Keep no_show_count and total_appointments in sync on the patient.

    Only completed and no_show appointments count toward the totals —
    pending/confirmed appointments haven't concluded yet.
    """
    old = getattr(instance, '_old_status', None)
    new = instance.status

    if old == new:
        return

    patient = instance.patient

    # Moving INTO a counted status
    if new in COUNTED_STATUSES and old not in COUNTED_STATUSES:
        patient.total_appointments += 1
        if new == 'no_show':
            patient.no_show_count += 1

    # Moving OUT OF a counted status (e.g. a correction)
    elif old in COUNTED_STATUSES and new not in COUNTED_STATUSES:
        patient.total_appointments = max(0, patient.total_appointments - 1)
        if old == 'no_show':
            patient.no_show_count = max(0, patient.no_show_count - 1)

    # Switching between counted statuses (completed → no_show or vice versa)
    elif old in COUNTED_STATUSES and new in COUNTED_STATUSES:
        if new == 'no_show':
            patient.no_show_count += 1
        elif old == 'no_show':
            patient.no_show_count = max(0, patient.no_show_count - 1)

    patient.save(update_fields=['no_show_count', 'total_appointments'])
