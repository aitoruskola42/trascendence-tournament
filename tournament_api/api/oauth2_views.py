from django.http import JsonResponse  # Provides a JSON-formatted HTTP response
from oauth2_provider.models import Application  # OAuth2 application model
from django.contrib.auth.models import User  # Django's built-in User model
from django.views.decorators.csrf import csrf_exempt  # Decorator to exempt views from CSRF protection
import json  # Provides JSON encoding and decoding functionality

@csrf_exempt
def create_oauth2_app(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = User.objects.get(username=data['username'])
        app = Application.objects.create(
            user=user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            name=data['name'],
            redirect_uris=data['redirect_uris']
        )
        return JsonResponse({
            'client_id': app.client_id,
            'client_secret': app.client_secret,
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)
