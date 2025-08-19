from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib import messages
from django.middleware.csrf import get_token

class SessionSecurityMiddleware:
    """
    Middleware to ensure proper session handling and prevent unauthorized access
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that require authentication
        protected_urls = [
            '/student/dashboard/',
            '/admin-panel/',
        ]
        
        # Check if the current path requires authentication
        requires_auth = any(request.path.startswith(url) for url in protected_urls)
        
        if requires_auth and not request.user.is_authenticated:
            # User is trying to access protected page without authentication
            return HttpResponseRedirect(reverse('student_login'))
        
        # If user is authenticated, check if they have proper permissions
        if request.user.is_authenticated:
            if request.path.startswith('/student/dashboard/'):
                if not hasattr(request.user, 'studentprofile'):
                    # Store a message in session before logout
                    messages.error(request, 'Access denied. Invalid session.')
                    logout(request)
                    return HttpResponseRedirect(reverse('student_login'))
            
            elif request.path.startswith('/admin-panel/'):
                if not (request.user.is_staff or request.user.is_superuser):
                    # Store a message in session before logout
                    messages.error(request, 'Access denied. Insufficient permissions.')
                    logout(request)
                    return HttpResponseRedirect(reverse('student_login'))

        response = self.get_response(request)
        
        # Add cache control headers for authenticated pages
        if requires_auth and request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Frame-Options'] = 'DENY'
            # Don't interfere with CSRF headers
        
        return response

class LogoutRedirectMiddleware:
    """
    Middleware to handle logout redirects properly
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request first
        response = self.get_response(request)
        
        # If user just logged out, ensure they can't use back button
        if not request.user.is_authenticated and request.session.get('just_logged_out', False):
            # Clear the flag
            if 'just_logged_out' in request.session:
                del request.session['just_logged_out']
            # Add headers to prevent caching
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response