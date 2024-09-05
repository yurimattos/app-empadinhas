from django.contrib import admin
from .models import User, UserTypes

admin.site.register(User)
admin.site.register(UserTypes)