from django.contrib.admin import site
from userprofile.models import UserProfile, Cooperative

site.register(UserProfile)
site.register(Cooperative)
