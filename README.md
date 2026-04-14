# Hospital Management Platform with AI chatbot

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Django 5 + Django REST Framework |
| Database | PostgreSQL 16 |
| Auth | JWT (SimpleJWT) + TOTP MFA |
| Encryption | Fernet / AES-128 (field-level) |


---

A full-stack web platform that digitizes and streamlines hospital operations — from patient registration and medical records to appointment scheduling and doctor-patient communication.

## What it does

**For patients**, the platform provides a secure personal portal where they can register, manage their health profile, view their medical history and prescriptions, and book appointments with doctors. An AI-powered chatbot helps patients describe their symptoms and get directed to the right specialist, with the option to schedule a consultation directly from the chat.

**For doctors**, the platform provides a dashboard to manage their daily schedule, access patient records, write consultation notes and prescriptions, and refer patients to other departments.

**For hospital staff and administrators**, the platform offers tools to manage staff accounts, monitor appointments across all departments, oversee billing and invoicing, and track pharmacy inventory.

All patient health data — including medical records, diagnoses, and prescriptions — is encrypted at rest, ensuring privacy and compliance with healthcare data protection standards.

## Core features

- AI chatbot for symptom triage and appointment booking
- Secure patient registration and health profiles
- Encrypted medical records, prescriptions, and lab results
- Real-time appointment scheduling with doctor availability
- Doctor dashboard with patient queue and consultation notes
- Admin panel for staff, department, and billing management
- Email and SMS appointment reminders
- Role-based access control (patient, doctor, nurse, receptionist, admin)

