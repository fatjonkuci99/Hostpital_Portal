from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .utils import get_user_from_cookie


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _set_jwt_cookies(response, user):
    refresh = RefreshToken.for_user(user)
    response.set_cookie(
        'access', str(refresh.access_token),
        max_age=15 * 60, httponly=True, samesite='Lax',
    )
    response.set_cookie(
        'refresh', str(refresh),
        max_age=7 * 24 * 3600, httponly=True, samesite='Lax',
    )
    return response


# ─── API Views ────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'detail': 'Logged out successfully.'})
    except Exception:
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


# ─── Template Views ────────────────────────────────────────────────────────────

def home_page(request):
    return render(request, 'home.html')


def login_page(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            email    = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            user = authenticate(request, username=email, password=password)
            if user and user.is_active:
                if user.role != User.PATIENT:
                    return render(request, 'login.html', {
                        'tab':         'login',
                        'login_error': 'Staff accounts must use the staff login portal.',
                        'login_email': email,
                    })
                response = redirect('dashboard')
                return _set_jwt_cookies(response, user)
            return render(request, 'login.html', {
                'tab':         'login',
                'login_error': 'Invalid email or password.',
                'login_email': email,
            })

        if action == 'register':
            data = {
                'email':      request.POST.get('email', '').strip(),
                'first_name': request.POST.get('first_name', '').strip(),
                'last_name':  request.POST.get('last_name', '').strip(),
                'password':   request.POST.get('password', ''),
                'password2':  request.POST.get('password2', ''),
            }
            serializer = RegisterSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                response = redirect('dashboard')
                return _set_jwt_cookies(response, user)
            errors = serializer.errors
            error_msg = next(iter(errors.values()))[0] if errors else 'Registration failed.'
            return render(request, 'login.html', {
                'tab':            'register',
                'register_error': str(error_msg),
                'reg_first':      data['first_name'],
                'reg_last':       data['last_name'],
                'reg_email':      data['email'],
            })

    return render(request, 'login.html', {'tab': 'login'})


def staff_login_page(request):
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user and user.is_active:
            if user.role == User.PATIENT:
                return render(request, 'staff_login.html', {
                    'error': 'Patient accounts must use the patient login portal.',
                    'email': email,
                })
            response = redirect('dashboard')
            return _set_jwt_cookies(response, user)
        return render(request, 'staff_login.html', {
            'error': 'Invalid email or password.',
            'email': email,
        })
    return render(request, 'staff_login.html')


def logout_page(request):
    refresh_str = request.COOKIES.get('refresh')
    if refresh_str:
        try:
            RefreshToken(refresh_str).blacklist()
        except TokenError:
            pass
    response = redirect('home')
    response.delete_cookie('access')
    response.delete_cookie('refresh')
    return response


def dashboard_router(request):
    user = get_user_from_cookie(request)
    if not user:
        return redirect('login')

    context = {'user': user}

    if user.role == User.PATIENT:
        return render(request, 'dashboard_patient.html', context)
    elif user.role == User.DOCTOR:
        return render(request, 'dashboard_doctor.html', context)
    elif user.role in User.STAFF_ROLES:
        return render(request, 'dashboard_staff.html', context)

    return redirect('login')
