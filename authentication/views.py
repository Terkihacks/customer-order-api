from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from .auth_utils import oauth
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view


@api_view(['POST'])
def register(request):
    # Register a new user.
    data = request.data
    username = data.get("name")
    password = data.get("password")
    email = data.get("email")
    
    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)
    user = User.objects.create_user(username=username, password=password, email=email)
    return JsonResponse({"message": "User registered successfully"}, status=201)

@csrf_exempt
def token_refresh(request):
    """
    Refresh JWT access token.
    """
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return JsonResponse({"error": "Refresh token required"}, status=400)
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        return JsonResponse({"access": access_token})
    except Exception:
        return JsonResponse({"error": "Invalid refresh token"}, status=400)

def login(request):
    # http://localhost:8000/api/v1/auth/callback/
    redirect_uri = "http://localhost:8000/api/v1/auth/callback/"
    return oauth.auth0.authorize_redirect(request, redirect_uri)

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    user_info = token.get("userinfo")
    request.session["user"] = user_info
    return JsonResponse(user_info)
    return ""

def logout(request):
    request.session.clear()
    return redirect(
        f"https://{settings.OIDC_OP_DISCOVERY_ENDPOINT}/v2/logout?"
        f"client_id={settings.OIDC_RP_CLIENT_ID}&returnTo=http://localhost:8000/"
    )
