from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User


def get_user_from_cookie(request):
    token_str = request.COOKIES.get('access')
    if not token_str:
        return None
    try:
        token = AccessToken(token_str)
        return User.objects.get(id=token['user_id'])
    except (TokenError, User.DoesNotExist):
        return None
