from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from .auth_utils import oauth
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework import status
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["POST"])
def register(request):
    """
    Register a new customer.
    POST JSON:
    {
        "email": "test@example.com",
        "name": "John Doe",
        "password": "strongpass123",
        "phone": "+254712345678"  # optional
    }
    """
    data = request.data
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")
    phone = data.get("phone", None)

    if not email or not password:
        return Response(
            {"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if Customer.objects.filter(email=email).exists():
        return Response({"error": "Customer with this email already exists"}, status=400)

    customer = Customer.objects.create_user(email=email, name=name, password=password, code=email, phone=phone)

    return Response(
        {
            "message": "Customer registered successfully",
            "customer": {"id": customer.id, "email": customer.email, "name": customer.name, "phone": customer.phone},
        },
        status=status.HTTP_201_CREATED,
    )
    
# @csrf_exempt
@api_view(["POST"])
def token_refresh(request):
    """
    Refresh JWT access token.
    """
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"error": "No refresh token provided"}, status=status.HTTP_400_BAD_REQUEST)
        # return JsonResponse({"error": "Refresh token required"}, status=400)
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

    email = user_info.get("email")
    sub = user_info.get("sub")  # unique Auth0 user id
    name = user_info.get("name", email.split("@")[0])

    # Create or fetch Django user
    user, created = User.objects.get_or_create(
        username=sub,
        defaults={"email": email, "first_name": name}
    )

    # Save Auth0 session
    request.session["user"] = {
        "id": user.id,
        "email": user.email,
        "auth0_sub": sub,
    }

    return Response({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.first_name,
        },
        "token": token  
    })

def logout(request):
    request.session.clear()
    return redirect(
        f"https://{settings.OIDC_OP_DISCOVERY_ENDPOINT}/v2/logout?"
        f"client_id={settings.OIDC_RP_CLIENT_ID}&returnTo=http://localhost:8000/"
    )
