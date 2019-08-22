"""
Company (Model)
"""
import datetime
from datetime import datetime as dte
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from bracketline.models import CountryMaster, StateMaster 


class Organisation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="organisation_owner", on_delete=models.CASCADE)
    counter = models.IntegerField(blank=True)
    url_hash = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=50, blank=False)
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    address = models.TextField(blank=True)
    country = models.ForeignKey(CountryMaster, on_delete=models.DO_NOTHING, default=12, related_name="company_country")
    state = models.ForeignKey(StateMaster, on_delete=models.DO_NOTHING, related_name='company_state')
    telephone_no = models.CharField(max_length=32, blank=True, null=True)
    mobile_no = models.CharField(max_length=32, blank=True, null=True)
    logo = models.ImageField(upload_to='organisation/logo', blank=True, null=True)
    cover = models.ImageField(upload_to='organisation/cover', blank=True, null=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.id:
            self.modified_date = datetime.datetime.now()
        else:
            self.created_date = datetime.datetime.now()

        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + \
                    str(self.user.id) + '-' + 'P' + '-' + \
                    '1' + '-' + 'O' + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + \
                    str(self.user.id) + '-' + 'P' + '-' + \
                    '1' + '-' + 'O' + str(self.counter)

        try:
            this = Organisation.objects.get(id=self.id)
            if this.logo != self.logo:
                this.logo.delete()
        except:
            pass

        if self.logo:
            imageTemproary = Image.open(self.logo)
            outputIoStream = BytesIO()
            imageTemproaryResized = imageTemproary.resize((300, 300))
            imageTemproaryResized.save(
                outputIoStream, format='JPEG', quality=150)
            outputIoStream.seek(0)
            self.logo = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % self.logo.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)

        if self.cover:
            imageTemproary = Image.open(self.cover)
            outputIoStream = BytesIO()
            imageTemproaryResized = imageTemproary.resize((300, 300))
            imageTemproaryResized.save(
                outputIoStream, format='JPEG', quality=150)
            outputIoStream.seek(0)
            self.cover = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % self.logo.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
        super(Organisation, self).save(*args, **kwargs)


    class Meta:
        ordering = ["name"]



class Company(models.Model):
    """
    Company Model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="company_owner", on_delete=models.CASCADE)
    counter = models.IntegerField(blank=True)
    url_hash = models.CharField(max_length=100, null=True, blank=True)
    organisation = models.OneToOneField(Organisation, related_name='company_organisation', on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    types = (
             ('Individual', 'Individual'),
             ('HUF', 'HUF'),
             ('Partnership', 'Partnership'),
             ('Trust', 'Trust'),
             ('Private Company', 'Private Company'),
             ('Public Company', 'Public Company'),
             ('LLP', 'LLP'),
             )
    nature = (
              ('Service Provider', 'Service Provider'),
              ('Retail', 'Retail'),
              ('Wholesale', 'Wholesale'),
              ('Works Contract', 'Works Contract'),
              ('Leasing', 'Leasing'),
              ('Factory Manufacturing', 'Factory Manufacturing'),
              ('Bonded Warehouse', 'Bonded Warehouse'),
              )
    bussiness_nature = models.CharField(max_length=32, choices=nature, default='Retail')
    invetory = (
        ('Accounts Only', 'Accounts Only'),
        ('Accounts with Inventory', 'Accounts with Inventory'),
    )
    maintain = models.CharField(max_length=32, choices=invetory, default='Accounts with Inventory')
    type_of_company = models.CharField(max_length=32, choices=types, default='Individual')
    # address = models.TextField(blank=True)
    # country = models.ForeignKey(CountryMaster, on_delete=models.DO_NOTHING, default=12, related_name="company_country")
    # state = models.ForeignKey(StateMaster, on_delete=models.DO_NOTHING, related_name='company_state')
    # pin_code = models.CharField(max_length=32)
    # telephone_no = models.CharField(max_length=32, blank=True, null=True)
    # mobile_no = models.CharField(max_length=32, blank=True, null=True)

    financial_date = (
        ("1st:April-31st:March", "1st:April-31st:March"),
        ("1st:Jan-31st:December", "1st:Jan-31st:December")
    )
    financial_year_from = models.CharField(
        max_length=30,
        choices=financial_date,
        default="1st:April-31st:March",
        blank=False)
    books_begining_from = models.DateField(default=datetime.date.today)
    gst = models.CharField(max_length=20, blank=True, null=True)
    bool_list = (
        ("Yes", "Yes"),
        ("No", "No")
    )
    gst_enabled = models.CharField(
        max_length=3, choices=bool_list, default="No", blank=False)
    types = (
        ("Regular", "Regular"),
        ("Composition", "Composition")
    )
    gst_registration_type = models.CharField(max_length=20, choices=types, default="Regular", blank=False)
    pan_no = models.CharField(max_length=18, blank=True, null=True)
    auditor = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='main_auditor', blank=True)
    accountant = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='main_accountant', blank=True)
    purchase_personel = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='main_purchase', blank=True)
    sale_personel = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='main_sales', blank=True)
    cb_personal = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='main_cb', blank=True)
    capital = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    asset = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    pl = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    is_other_territory = models.BooleanField(default=False)
    way_bill = models.CharField(max_length=3, choices=bool_list, default='No')
    includes = (
        ('Invoice value', 'Invoice value'),
        ('Taxable and exemt goods value', 'Taxable and exemt goods value'),
        ('Taxable goods value', 'Taxable goods value'),
    )
    threshold_limit_inc = models.CharField(max_length=50, choices=includes, default='Invoice value', blank=True)
    interstate_apl = models.CharField(max_length=3, choices=bool_list, default='No', blank=True)
    threshold_limit = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    intrastate_apl = models.CharField(max_length=3, choices=bool_list, default='No', blank=True)
    threshold_limit_intra = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    adv_receipt_tax = models.BooleanField(default=False)
    tax_liability = models.BooleanField(default=False)
    set_or_alter_gst = models.CharField(max_length=100, choices=bool_list, default='No', blank=True)
    hsn = models.CharField(max_length=15, blank=True)
    tax_cat = (
        ('Unknown', 'Unknown'),
        ('Exempt', 'Exempt'),
        ('Nil Rated', 'Nil Rated'),
        ('Taxable', 'Taxable'),
    )
    taxability = models.CharField(max_length=20, choices=tax_cat, default='Unknown')
    reverse_charge = models.CharField(max_length=3, choices=bool_list, default='No', blank=True)
    input_credit = models.CharField(max_length=3, choices=bool_list, default='No', blank=True)
    integrated_tax = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    central_tax = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    state_tax = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    cess = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    provide_lut = models.CharField(max_length=3, choices=bool_list, default='No', blank=True)
    lut_bond_no = models.CharField(max_length=50, blank=True)
    gst_applicable = models.DateField(default=datetime.date.today)
    applicable_from = models.DateField(default=datetime.date.today)
    applicable_to = models.DateField(default=datetime.date.today)
    tax_rate = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    purchase_tax = models.CharField(max_length=3, choices=bool_list, default='No', blank=True)

    def __str__(self):
        return "{}-{}".format(self.organisation.name, self.url_hash)

    # def clean(self):
    #     if not self.gst_enabled and self.gst_registration_type == "Composition":
    #         error_result = {'gst_enabled': ["To enable composite billing GST should be enabled"], 'gst_registration_type': [
    #             "To enable composite billing GST should be enabled"]}
    #         raise ValidationError(error_result)

    def save(self, **kwargs):
        if self.id:
            self.modified_date = datetime.datetime.now()
        else:
            self.created_date = datetime.datetime.now()

        if not self.url_hash:
            if self.user.profile.user_type == 'Bussiness User':
                self.url_hash = 'BU' + '-' + \
                    str(self.user.id) + '-' + 'P' + '-' + \
                    '1' + '-' + 'C' + str(self.counter)
            else:
                self.url_hash = 'PU' + '-' + \
                    str(self.user.id) + '-' + 'P' + '-' + \
                    '1' + '-' + 'C' + str(self.counter)
        super(Company, self).save()



class StaticPage(models.Model):
    '''
    static page model
    '''
    organisation = models.OneToOneField(Organisation, related_name="organization_static_page",
                                on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    title1 = models.TextField(blank=True, null=True)
    title2 = models.TextField(blank=True, null=True)
    facebook_url = models.URLField(max_length=200, blank=True, null=True)
    twitter_url = models.URLField(max_length=200, blank=True, null=True)
    linkedin_url = models.URLField(max_length=200, blank=True, null=True)
    service_desc = models.TextField(blank=True, null=True)
    portfolio_desc = models.TextField(blank=True, null=True)
    team_desc = models.TextField(blank=True, null=True)
    head_bg = models.ImageField(
        upload_to='static_page/head_img', null=True, blank=True)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('static-page', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        try:
            this = StaticPage.objects.get(id=self.id)
            if this.head_bg != self.head_bg:
                this.head_bg.delete()
        except:
            pass

        if self.head_bg:
            imageTemproary = Image.open(self.head_bg)
            outputIoStream = BytesIO()
            imageTemproaryResized = imageTemproary.resize((1349, 690))
            imageTemproaryResized.save(
                outputIoStream, format='JPEG', quality=250)
            outputIoStream.seek(0)
            self.head_bg = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % self.head_bg.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
        super(StaticPage, self).save(*args, **kwargs)

class Service(models.Model):
    '''
    services is child model of static pages 
    list of services of conpany
    '''
    staticpage = models.ForeignKey(StaticPage, related_name="static_page_service",
                                on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    desc = models.TextField(null=True, blank=True)
    icon = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('static-page', kwargs={'pk': self.pk})

    def save(self):
        super().save()

class Portfolio(models.Model):
    '''
    Portfolio is child model of static pages 
    list of Portfolio of conpany
    '''
    staticpage = models.ForeignKey(StaticPage, related_name="static_page_portfolio",
                                on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    desc = models.TextField(null=True, blank=True)
    image = models.ImageField(
        upload_to='static_page/portfolio', null=True, blank=True)

    def __str__(self):
        return self.name



    def save(self, *args, **kwargs):
        try:
            this = Portfolio.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except:
            pass

        if self.image:
            imageTemproary = Image.open(self.image)
            outputIoStream = BytesIO()
            imageTemproaryResized = imageTemproary.resize((350, 262))
            imageTemproaryResized.save(
                outputIoStream, format='JPEG', quality=150)
            outputIoStream.seek(0)
            self.image = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % self.image.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
        super(Portfolio, self).save(*args, **kwargs)

class TeamMember(models.Model):
    '''
    TeamMember is child model of static pages 
    list of TeamMember of organisation
    '''
    staticpage = models.ForeignKey(StaticPage, related_name="static_page_teammember",
                                on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100,blank=True)
    profession = models.CharField(max_length=100,null=True, blank=True)
    pic = models.ImageField(
        upload_to='static_page/team', null=True, blank=True)
    facebook_url = models.URLField(max_length=200, blank=True, null=True)
    twitter_url = models.URLField(max_length=200, blank=True, null=True)
    linkedin_url = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('static-page', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        try:
            this = TeamMember.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except:
            pass

        if self.pic:
            imageTemproary = Image.open(self.pic)
            outputIoStream = BytesIO()
            imageTemproaryResized = imageTemproary.resize((225, 225))
            imageTemproaryResized.save(
                outputIoStream, format='JPEG', quality=150)
            outputIoStream.seek(0)
            self.pic = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % self.pic.name.split(
                '.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)
        super(TeamMember, self).save(*args, **kwargs)