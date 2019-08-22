from django.db import models
from django.conf import settings
from django.utils import timezone
from sorl.thumbnail import ImageField

from company.models import Organisation

# Create your models here.


class EmployeeMasterQR(models.Model):
    """
    Employee Master Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Organisation, on_delete=models.CASCADE,
                                null=True, blank=True, related_name='Company_employee')
    counter = models.IntegerField(blank=True, null=True)
    url_hash = models.CharField(max_length=100, null=True, blank=True)
    employee_name = models.CharField(max_length=200)
    post = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=12)
    email = models.EmailField(
        max_length=100, null=True, blank=True, unique=True)
    salary = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    joining_date = models.DateField(default=timezone.now)
    qr_code = ImageField(upload_to='qr_images', null=True, blank=True)
    is_qr = models.BooleanField(default=False)

    def __str__(self):
        return self.employee_name

    def save(self, *args, **kwargs):
        """
        Save function to delete the bar code image whenever updated and to create a url_hash
        """
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SQR') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SQR') + str(self.counter)

        self.salary = round(self.salary, 2)

        super(EmployeeMasterQR, self).save(*args, **kwargs)


class StockMasterQR(models.Model):
    """
    Stock Master QR model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Organisation, on_delete=models.CASCADE,
                                null=True, blank=True, related_name='Company_stock_master')
    counter = models.IntegerField(blank=True, null=True)
    url_hash = models.CharField(max_length=100, null=True, blank=True)
    stock_name = models.CharField(max_length=32)
    batch_no = models.PositiveIntegerField(blank=True, null=True)
    bar_code = ImageField(upload_to='stockmanagement', null=True, blank=True)
    mnf_date = models.DateField(blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    qr_code = ImageField(upload_to='qr_images', null=True, blank=True)
    is_qr = models.BooleanField(default=False)

    def __str__(self):
        return str(self.stock_name)

    def save(self, *args, **kwargs):
        """
        Save function to delete the bar code image whenever updated and to create a url_hash
        """
        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SQR') + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + str(self.user.id) + '-' + 'P' + '-' + '1' + '-' + 'C' + str(
                    self.company.counter) + '-' + ('SQR') + str(self.counter)

        try:
            this = StockMasterQR.objects.get(id=self.id)
            if this.bar_code != self.bar_code:
                this.bar_code.delete()
        except:
            pass
        super(StockMasterQR, self).save(*args, **kwargs)
