from django.contrib import admin

# Register your models here.
from .models import Member, Leader, Space, Branch, Report

admin.site.register(Member)
admin.site.register(Leader)
admin.site.register(Space)
admin.site.register(Branch)
admin.site.register(Report)
