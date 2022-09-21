from django.db import models
# Create your models here.


class Member(models.Model):
    member_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=255, null=False)
    role = models.CharField(
        default="Member", max_length=100, null=False, blank=True)
    space = models.ManyToManyField(
        'Space', related_name='members', blank=True)
    photo = models.ImageField(upload_to='profile_pics', blank=True,
                              null=False, default='profile_pics/default_member.png')
    branch = models.ForeignKey(
        'Branch', on_delete=models.CASCADE, null=False, blank=False, related_name='members')

    def delete(self, *args, **kwargs):
        if self.photo != 'profile_pics/default_member.png':
            self.photo.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Members'

    def __str__(self):
        return self.name


class Leader(models.Model):
    leader_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=255, null=False)
    branch = models.ForeignKey(
        'Branch', on_delete=models.CASCADE, null=False, related_name='leader')
    role = models.CharField(
        default="Leader", max_length=100, null=False, blank=True)
    photo = models.ImageField(upload_to='profile_pics', blank=True,
                              null=False, default='profile_pics/default_leader.png')

    def delete(self, *args, **kwargs):
        if self.photo != 'profile_pics/default_leader.png':
            self.photo.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Leader'

    def __str__(self):
        return self.name


class Branch(models.Model):
    branch_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Branches'

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()

    def leader_count(self):
        return self.leader.count()

    def space_count(self):
        return self.spaces.count()


class Space(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, null=False, unique=True)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, null=False, related_name='spaces')
    leader = models.ForeignKey(
        Leader, on_delete=models.SET_NULL, null=True, blank=True)
    memberKey = models.IntegerField(null=False, unique=True)
    leaderKey = models.IntegerField(null=False, unique=True)

    class Meta:
        unique_together = ('code', 'branch', 'name')
        verbose_name_plural = "Spaces"

    def __str__(self):
        return self.name


class Announcement(models.Model):
    space_code = models.ForeignKey(
        Space, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(max_length=2000, null=False)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    file = models.FileField(upload_to='announcement_files', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Announcements"
        ordering = ['-datetime']

    def __str__(self):
        return self.title

    def post_date(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")


class Report(models.Model):
    space_code = models.ForeignKey(
        Space, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(max_length=2000, null=False)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    deadline = models.DateTimeField(null=False)
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    marks = models.DecimalField(max_digits=6, decimal_places=2, null=False)

    class Meta:
        verbose_name_plural = "Reports"
        ordering = ['-datetime']

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def post_date(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")

    def due_date(self):
        return self.deadline.strftime("%d-%b-%y, %I:%M %p")


class Submission(models.Model):
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, null=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=False)
    file = models.FileField(upload_to='submissions/', null=True,)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    marks = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)

    def file_name(self):
        return self.file.name.split('/')[-1]

    def time_difference(self):
        difference = self.report.deadline - self.datetime
        days = difference.days
        hours = difference.seconds//3600
        minutes = (difference.seconds//60) % 60
        seconds = difference.seconds % 60

        if days == 0:
            if hours == 0:
                if minutes == 0:
                    return str(seconds) + " seconds"
                else:
                    return str(minutes) + " minutes " + str(seconds) + " seconds"
            else:
                return str(hours) + " hours " + str(minutes) + " minutes " + str(seconds) + " seconds"
        else:
            return str(days) + " days " + str(hours) + " hours " + str(minutes) + " minutes " + str(seconds) + " seconds"

    def submission_date(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.member.name + " - " + self.report.title

    class Meta:
        unique_together = ('report', 'member')
        verbose_name_plural = "Submissions"
        ordering = ['datetime']


class Coupon(models.Model):
    space_code = models.ForeignKey(
        Space, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(max_length=2000, null=False)
    datetime = models.DateTimeField(auto_now_add=True, null=False)
    file = models.FileField(upload_to='coupons/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Coupons"
        ordering = ['-datetime']

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def post_date(self):
        return self.datetime.strftime("%d-%b-%y, %I:%M %p")
