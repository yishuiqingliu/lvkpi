# coding=utf-8

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.utils.encoding import force_str
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils.six.moves.urllib.parse import urlparse

from SSO.models import *
from re import compile
import logging

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

def user_passes_test(request, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
  if not request.user.is_authenticated():
    path = request.build_absolute_uri()
    resolved_login_url = force_str(resolve_url(login_url or settings.LOGIN_URL))
    
    login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
    current_scheme, current_netloc = urlparse(path)[:2]
    if ((not login_scheme or login_scheme == current_scheme) and
        (not login_netloc or login_netloc == current_netloc)):
        path = request.get_full_path()
    from django.contrib.auth.views import redirect_to_login
    return redirect_to_login(
        path, resolved_login_url, redirect_field_name)

class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """
    def process_request(self, request):
        assert hasattr(request, 'user'), "The Login Required middleware\
         requires authentication middleware to be installed. Edit your\
         MIDDLEWARE_CLASSES setting to insert\
         'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
         work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
         'django.core.context_processors.auth'."
        path = request.path_info.lstrip('/')
        if not any(m.match(path) for m in EXEMPT_URLS):
          return user_passes_test(request)
