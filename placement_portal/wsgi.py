"""
WSGI config for placement_portal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
import traceback

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_portal.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    sys.stderr.write("!!! CRITICAL: Django WSGI initialization failed !!!\n")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    raise e
