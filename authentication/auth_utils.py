from authlib.integrations.django_client import OAuth
from django.conf import settings

oauth = OAuth()

oauth.register(
    name="auth0",
    client_id=settings.OIDC_RP_CLIENT_ID,
    client_secret=settings.OIDC_RP_CLIENT_SECRET,
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f"https://{settings.OIDC_OP_DISCOVERY_ENDPOINT}/.well-known/openid-configuration",
    redirect_uri="http://localhost:8000/api/v1/auth/callback/",
)
