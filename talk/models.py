from django.db import models
from main.models import Member, Leader, Space

class LeaderTalk(models.Model):
    content = models.TextField(max_length=2000, null=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='spaceTalks')
    sent_by = models.ForeignKey(
        Leader, on_delete=models.CASCADE, related_name='spaceTalks')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def time(self):
        return self.sent_at.strftime("%d-%b-%y, %I:%M %p")

    def __str__(self):
        return self.content[:30]

class MemberTalk(models.Model):
    content = models.TextField(max_length=2000, null=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='talks')
    sent_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='talks')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def time(self):
        return self.sent_at.strftime("%d-%b-%y, %I:%M %p")

    def __str__(self):
        return self.content[:30]
