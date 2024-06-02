"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
from whitenoise import WhiteNoise  # type: ignore

os.makedirs("staticfiles", exist_ok=True)  # fix: no directory warning
application = get_wsgi_application()
application = WhiteNoise(application, root="staticfiles")
