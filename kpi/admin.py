from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from kpi.models import *

class AccountInline(admin.StackedInline):
  model = Account
  can_delete = True
  verbose_name_plural = 'account'

class UserAdmin(UserAdmin):
  inlines = (AccountInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Role)
admin.site.register(Permission)