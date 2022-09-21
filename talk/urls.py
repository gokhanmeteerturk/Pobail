from django.urls import path
from . import views

urlpatterns = [
    path('talk/<int:code>', views.talk, name='talk'),
    path('send/<int:code>/<int:std_id>', views.send, name='send'),
    path('message/<int:code>/<int:fac_id>', views.send_fac, name='send_fac'),
]