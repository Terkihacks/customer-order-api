from django.http import JsonResponse
from django.conf import settings
from authlib.jose import JsonWebToken, JoseError
from authlib.jose.errors import ExpiredTokenError
import requests

class Auth0Middleware:
    """
    Middleware to protect /api/ routes using Auth0 JWT validation with Authlib.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        self.jwks = requests.get(self.jwks_url).json()
        self.jwt = JsonWebToken(['RS256'])

    def __call__(self, request):
        if request.path.startswith("/api/"):  # only protect API routes
            auth_header = request.headers.get("Authorization", None)
            if not auth_header:
                return JsonResponse({"error": "Authorization header missing"}, status=401)

            try:
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    return JsonResponse({"error": "Invalid token type"}, status=401)
            except ValueError:
                return JsonResponse({"error": "Invalid Authorization header"}, status=401)

            try:
                claims = self.jwt.decode(
                    token,
                    self.jwks,
                    claims_options={
                        "iss": {"essential": True, "value": f"https://{settings.AUTH0_DOMAIN}/"},
                        "aud": {"essential": True, "value": settings.OIDC_RP_CLIENT_ID}
                    }
                )
                claims.validate() 

                request.auth_payload = claims  # attach claims to request

            except ExpiredTokenError:
                return JsonResponse({"error": "Token expired"}, status=401)
            except JoseError as e:
                return JsonResponse({"error": f"Invalid token: {str(e)}"}, status=401)

        return self.get_response(request)
