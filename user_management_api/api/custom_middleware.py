import json 
from django.utils.deprecation import MiddlewareMixin 

class TokenRequestPrintMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path == '/api/token/' and request.method == 'POST':
            print(f"Login attempt for user: {request.POST.get('username')}")
            
    def process_response(self, request, response):
        if request.path == '/api/token/' and request.method == 'POST':
            if response.status_code == 200:
                print("Response data to be sent to frontend:")
                print(json.dumps(json.loads(response.content.decode('utf-8')), indent=2))
            else:
                print(f"Login failed. Status code: {response.status_code}")
        return response