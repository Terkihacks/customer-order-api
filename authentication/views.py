from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from .auth_utils import oauth

def login(request):
    # http://localhost:8000/api/v1/auth/callback/
    redirect_uri = "http://localhost:8000/api/v1/auth/callback/"
    return oauth.auth0.authorize_redirect(request, redirect_uri)

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    user_info = token.get("userinfo")
    request.session["user"] = user_info
    return JsonResponse(user_info)

def logout(request):
    request.session.clear()
    return redirect(
        f"https://{settings.OIDC_OP_DISCOVERY_ENDPOINT}/v2/logout?"
        f"client_id={settings.OIDC_RP_CLIENT_ID}&returnTo=http://localhost:8000/"
    )
