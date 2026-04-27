from django.contrib import admin
from .models import Appointment, MedicalRecord, Diagnosis, Prescription, LabResult, ImagingResult, DoctorSchedule, BlockedSlot


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = ['patient', 'doctor', 'date_time', 'reason', 'status']
    list_filter   = ['status']
    search_fields = ['patient__email', 'doctor__email', 'reason']


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display  = ['patient', 'doctor', 'date', 'appointment']
    search_fields = ['patient__email', 'doctor__email']


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display  = ['condition', 'severity', 'status', 'date_diagnosed', 'medical_record']
    list_filter   = ['severity', 'status']
    search_fields = ['condition', 'icd_code']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display  = ['medication', 'patient', 'doctor', 'dosage', 'status', 'start_date']
    list_filter   = ['status']
    search_fields = ['medication', 'patient__email']


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display  = ['test_name', 'patient', 'status', 'date']
    list_filter   = ['status']
    search_fields = ['test_name', 'patient__email']


@admin.register(ImagingResult)
class ImagingResultAdmin(admin.ModelAdmin):
    list_display  = ['imaging_type', 'body_part', 'patient', 'date']
    list_filter   = ['imaging_type']
    search_fields = ['body_part', 'patient__email']


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display  = ['doctor', 'weekday', 'start_time', 'end_time', 'slot_duration', 'specialty', 'is_active']
    list_filter   = ['weekday', 'is_active']
    search_fields = ['doctor__email', 'doctor__first_name', 'doctor__last_name', 'specialty']


@admin.register(BlockedSlot)
class BlockedSlotAdmin(admin.ModelAdmin):
    list_display  = ['doctor', 'date_time', 'reason']
    search_fields = ['doctor__email', 'doctor__first_name', 'doctor__last_name']
