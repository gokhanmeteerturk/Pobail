from django.contrib import admin
from . models import Quiz, Question, MemberAnswer



# Register models here.
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(MemberAnswer)
