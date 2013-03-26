import os, sys
# Bodge to remove shite from pythonpath. not sure why it's there in the first place.
sys.path = [s for s in sys.path if 'django/trunk' not in s]
sys.path.extend(['/var/www/django/ordercoops',
		 '/var/www/django/ordercoopsve',
		 '/var/www/django/ordercoopsve/ordercoops/',
		 '/var/www/django/ordercoopsve/lib/python2.6/site-packages',])

os.environ['DJANGO_SETTINGS_MODULE'] = 'ordercoops.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
