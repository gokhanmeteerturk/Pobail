from django.db import models
from main.models import Space, Member

class Attendance(models.Model):
    date = models.DateField(null=False, blank=False)
    status = models.BooleanField(default=False, blank=False, null=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.member.name + ' (' + self.space.name + ') ' + self.date.strftime('%Y-%m-%d')

    @staticmethod
    def reduce_is_set(thing_count):
        if thing_count == 0:
            return thing_count
        else:
            return thing_count - 1

    def total_absent(self):
        attendance = Attendance.objects.filter(
            member=self.member, status=False).count()
        return self.reduce_is_set(attendance)

    def total_present(self):
        present = Attendance.objects.filter(
            member=self.member, status=True).count()
        return self.reduce_is_set(present)
