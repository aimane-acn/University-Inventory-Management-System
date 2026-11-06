from django.contrib import messages
from django.shortcuts import redirect

class DemoProtectionMiddleware:
    """
    Blocks modifying POST requests (create, update, delete) for predefined demo accounts
    to prevent visitors from corrupting portfolio demo data.
    Allows full modifications for newly registered accounts.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            current_path = request.path.rstrip('/')
            if current_path == '':
                current_path = '/'

            # Allowed POST endpoints (login, logout, registration)
            is_auth_action = (
                current_path in ['/', '/signup', '/logout'] or
                (request.resolver_match and request.resolver_match.url_name in ['my_login', 'signup', 'logout'])
            )

            # Check if user is logged in as a predefined demo account
            if not is_auth_action and request.session.get('is_demo', False):
                messages.warning(
                    request,
                    "⚠️ Mode Démonstration : Les modifications (ajout, modification, suppression) sont bloquées "
                    "pour ce compte démo afin de préserver l'intégrité des données du portfolio. "
                    "Pour tester les ajouts et modifications réelles, veuillez créer votre propre compte via la page Inscription !"
                )
                referer = request.META.get('HTTP_REFERER')
                if referer:
                    return redirect(referer)
                return redirect(request.path)

        response = self.get_response(request)
        return response
