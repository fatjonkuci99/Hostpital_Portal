import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    PATIENT       = 'patient'
    DOCTOR        = 'doctor'
    NURSE         = 'nurse'
    RECEPTIONIST  = 'receptionist'
    ADMIN         = 'admin'
    LAB_STAFF     = 'lab_staff'
    IMAGING_STAFF = 'imaging_staff'

    ROLE_CHOICES = [
        (PATIENT,      'Patient'),
        (DOCTOR,       'Doctor'),
        (NURSE,        'Nurse'),
        (RECEPTIONIST, 'Receptionist'),
        (ADMIN,        'Admin'),
        (LAB_STAFF,    'Laboratory Staff'),
        (IMAGING_STAFF,'Imaging Staff'),
    ]

    # Staff roles (non-patient)
    STAFF_ROLES = {DOCTOR, NURSE, RECEPTIONIST, ADMIN, LAB_STAFF, IMAGING_STAFF}

    id                 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email              = models.EmailField(unique=True)
    first_name         = models.CharField(max_length=100)
    last_name          = models.CharField(max_length=100)
    role               = models.CharField(max_length=20, choices=ROLE_CHOICES, default=PATIENT)
    is_active          = models.BooleanField(default=True)
    is_staff           = models.BooleanField(default=False)
    created_at         = models.DateTimeField(auto_now_add=True)
    no_show_count      = models.PositiveIntegerField(default=0)
    total_appointments = models.PositiveIntegerField(default=0)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    objects = UserManager()

    def __str__(self):
        return f'{self.full_name} ({self.role})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_patient(self):
        return self.role == self.PATIENT

    @property
    def is_doctor(self):
        return self.role == self.DOCTOR

    @property
    def is_hospital_staff(self):
        return self.role in self.STAFF_ROLES
