import sys
from django.db import models
from datetime import datetime
import datetime
from django.utils import timezone
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from company.models import Organisation
from bracketline.models import StateMaster

class Job(models.Model):
    """
    Job model

    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="organisation_owner_job", on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, related_name='job_company_organisation', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='job_pic', null=True, blank=True)
    job_title = models.CharField(max_length=50)
    location = models.TextField(null=True, blank=True)
    job_function = models.CharField(max_length=50)
    emp_type = (
        ('Full-time', 'Full-time'),
        ('Permanent', 'Permanent'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
        ('Part-time', 'Part-time'),
    )
    employment_type = models.CharField(
        max_length=100, choices=emp_type, default='Choose')
    company_industry = models.CharField(max_length=50)
    seniorty_level = (
        ('Entry level', 'Entry level'),
        ('Associate', 'Associate'),
        ('Internship', 'Internship'),
        ('Mid-senior-level', 'Mid-senior-level'),
        ('Director', 'Director'),
        ('Executive', 'Executive'),
        ('Not Available', 'Not Available'),
    )
    seniority = models.CharField(
        max_length=100, choices=seniorty_level, default='Choose', blank=True, null=True)
    job_desc = RichTextUploadingField(
        blank=True, null=True, config_name='special')
    skills = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_title

    def get_absolute_url(self):
        return reverse('job:joblist')

    def save(self, *args, **kwargs):
        try:
            this = Job.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except:
            pass

        if self.image:
            imageTemproary = Image.open(self.image)
            outputIoStream = BytesIO()
            imageTemproaryResized = imageTemproary.resize((300, 300))
            imageTemproaryResized.save(
                outputIoStream, format='JPEG', quality=150)
            outputIoStream.seek(0)
            self.image = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % self.image.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
        super(Job, self).save(*args, **kwargs)


class Resume(models.Model):
    """
    Resume model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="organisation_owner_resume", on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='cv_pic', blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    state = models.ForeignKey(StateMaster, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='resume_state')
    email = models.CharField(max_length=32)
    mobile_no = models.CharField(max_length=32)
    degree = models.CharField(max_length=30)             # education info
    college = models.CharField(max_length=100)
    marks = models.CharField(blank=True, null=True, max_length=100)
    field_of_study = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50)
    time_period_from = models.DateField(blank=True, null=True)
    time_period_to = models.DateField(blank=True, null=True)
    working_experince = models.BooleanField(default=False)
    job_title = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    company_city = models.CharField(max_length=50, blank=True, null=True)
    experience_from = models.DateField(blank=True, null=True)
    experience_to = models.DateField(blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    desired_job_title = models.CharField(max_length=50, blank=True, null=True)
    job_Type = (
        ('Full-time', 'Full-time'),
        ('Permanent', 'Permanent'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
        ('Part-time', 'Part-time'),
    )
    desired_job_type = models.CharField(
        max_length=100, choices=job_Type, default='Choose')
    desired_salary = models.IntegerField(blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name

    def get_absolute_url(self):
        return reverse('resume', kwargs={'pk': self.pk})

    def save(self):
        super().save()
        if self.image:
            imageTemproary = Image.open(self.image)
            outputIoStream = BytesIO()
            imageTemproaryResized = imageTemproary.resize((100, 100))
            imageTemproaryResized.save(
                outputIoStream, format='JPEG', quality=150)
            outputIoStream.seek(0)
            self.image = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % self.image.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
        super(Resume, self).save()
