from django.conf import settings
from django.db import models


class Appointment(models.Model):
    PENDING   = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    NO_SHOW   = 'no_show'
    STATUS_CHOICES = [
        (PENDING,   'Pending'),
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
        (NO_SHOW,   'No Show'),
    ]

    patient    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_doctor')
    date_time  = models.DateTimeField()
    reason     = models.CharField(max_length=300)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_time']

    def __str__(self):
        return f'{self.patient} → Dr. {self.doctor} on {self.date_time:%Y-%m-%d %H:%M}'


class MedicalRecord(models.Model):
    patient     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_records')
    doctor      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_records')
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='medical_record')
    date        = models.DateField()
    summary     = models.TextField(blank=True)
    file        = models.FileField(upload_to='medical_records/', null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'Record — {self.patient} ({self.date})'


class Diagnosis(models.Model):
    MILD     = 'mild'
    MODERATE = 'moderate'
    SEVERE   = 'severe'
    SEVERITY_CHOICES = [
        (MILD,     'Mild'),
        (MODERATE, 'Moderate'),
        (SEVERE,   'Severe'),
    ]

    ACTIVE   = 'active'
    RESOLVED = 'resolved'
    CHRONIC  = 'chronic'
    STATUS_CHOICES = [
        (ACTIVE,   'Active'),
        (RESOLVED, 'Resolved'),
        (CHRONIC,  'Chronic'),
    ]

    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='diagnoses')
    condition      = models.CharField(max_length=200)
    icd_code       = models.CharField(max_length=20, blank=True)
    severity       = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    notes          = models.TextField(blank=True)
    date_diagnosed = models.DateField()

    def __str__(self):
        return f'{self.condition} ({self.status})'


class Prescription(models.Model):
    ACTIVE    = 'active'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (ACTIVE,    'Active'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    patient        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    doctor         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_prescriptions')
    medication     = models.CharField(max_length=200)
    dosage         = models.CharField(max_length=100)
    frequency      = models.CharField(max_length=100)
    start_date     = models.DateField()
    end_date       = models.DateField(null=True, blank=True)
    instructions   = models.TextField(blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.medication} for {self.patient}'


class LabResult(models.Model):
    PENDING = 'pending'
    NORMAL  = 'normal'
    FLAGGED = 'flagged'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (NORMAL,  'Normal'),
        (FLAGGED, 'Flagged'),
    ]

    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='lab_results')
    patient        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lab_results')
    test_name      = models.CharField(max_length=200)
    # Each key is a component name; value is {value, unit, reference, status}
    components     = models.JSONField(default=dict)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    date           = models.DateField()
    notes          = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.test_name} — {self.patient} ({self.date})'


class ImagingResult(models.Model):
    XRAY       = 'xray'
    MRI        = 'mri'
    CT         = 'ct'
    ULTRASOUND = 'ultrasound'
    TYPE_CHOICES = [
        (XRAY,       'X-Ray'),
        (MRI,        'MRI'),
        (CT,         'CT Scan'),
        (ULTRASOUND, 'Ultrasound'),
    ]

    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='imaging_results')
    patient        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='imaging_results')
    imaging_type   = models.CharField(max_length=20, choices=TYPE_CHOICES)
    body_part      = models.CharField(max_length=100)
    findings       = models.TextField()
    image_file     = models.FileField(upload_to='imaging/', null=True, blank=True)
    date           = models.DateField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.get_imaging_type_display()} — {self.body_part} ({self.patient})'


class DoctorSchedule(models.Model):
    WEEKDAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    doctor        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules')
    weekday       = models.IntegerField(choices=WEEKDAYS)
    start_time    = models.TimeField()
    end_time      = models.TimeField()
    slot_duration = models.PositiveIntegerField(help_text='Slot length in minutes (e.g. 15, 30, 60)')
    specialty     = models.CharField(max_length=100, blank=True)
    is_active     = models.BooleanField(default=True)

    class Meta:
        unique_together = ['doctor', 'weekday']

    def __str__(self):
        return f'Dr. {self.doctor} — {self.get_weekday_display()} ({self.slot_duration} min slots)'


class BlockedSlot(models.Model):
    doctor    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocked_slots')
    date_time = models.DateTimeField()
    reason    = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['doctor', 'date_time']

    def __str__(self):
        return f'Blocked — Dr. {self.doctor} at {self.date_time:%Y-%m-%d %H:%M}'
