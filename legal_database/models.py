"""
Models
"""
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Categories(models.Model):
    """
    Categories Model
    """
    types = (
        ('Forex & Banking', 'Forex & Banking'),
        ('Capital Market', 'Capital Market'),
        ('Corporate Laws', 'Corporate Laws'),
        ('Competition Laws', 'Competition Laws'),
        ('Indirect Taxation', 'Indirect Taxation'),
        ('Direct Taxation', 'Direct Taxation'),
        ('VAT', 'VAT'),
        ('Sales Tax', 'Sales Tax'),
        ('Compliance Almanac', 'Compliance Almanac'),
        ('Employment Laws', 'Employment Laws'),
        ('Labour', 'Labour'),
        ('Criminal Laws', 'Criminal Laws'),
        ('Insurance', 'Insurance'),
        ('Industrial & Service', 'Industrial & Service'),
        ('Human Rights', 'Human Rights'),
        ('Foreign Trade Policy', 'Foreign Trade Policy'),
        ('Indian Industrial Policy', 'Indian Industrial Policy'),
        ('Environment', 'Environment'),
        ('Intellectual Property Rights', 'Intellectual Property Rights'),
        ('Cyber & IT Laws', 'Cyber & IT Laws'),
        ('Media & Communication', 'Media & Communication'),
        ('Anti-Dumping', 'Anti-Dumping'),
        ('WTO', 'WTO'),
        ('Power & Energy', 'Power & Energy'),
        ('Mines & Minerals', 'Mines & Minerals'),
    )

    title = models.CharField(max_length=32, choices=types,
                             default='Forex & Banking', unique=True)

    def __str__(self):
        return self.title


class Cases(models.Model):
    """
    Cases Model
    """
    date = models.DateTimeField(auto_now_add=True)
    title = models.TextField(null=True, blank=True)
    bare_body = RichTextUploadingField(blank=True, config_name='special')
    summary = models.TextField(null=True, blank=True)
    facts = models.TextField(null=True, blank=True)
    issues = models.TextField(null=True, blank=True)
    ratio = models.TextField(null=True, blank=True)
    arguments = models.TextField(null=True, blank=True)
    judgement = models.TextField(null=True, blank=True)
    critics = models.TextField(null=True, blank=True)
    court = models.CharField(max_length=100, blank=True, null=True)
    sitations = models.TextField(null=True, blank=True)
    categories = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='Case_cat', blank=True)

    def __str__(self):
        return self.title


class CentralBareAct(models.Model):
    """
    Central Bare Act Model
    """
    date = models.DateTimeField(auto_now_add=True)
    title = models.TextField(null=True, blank=True)
    bare_body = RichTextUploadingField(
        blank=True, config_name='special')
    categories = models.ForeignKey(
        Categories, on_delete=models.CASCADE, related_name='cb_acts', blank=True)
    cases = models.ForeignKey(Cases, on_delete=models.CASCADE,
                              related_name='cb_acts_cases', blank=True)

    def __str__(self):
        return self.title


class StateBareAct(models.Model):
    """
    State Bare Act Model
    """
    date = models.DateTimeField(auto_now_add=True)
    title = models.TextField(null=True, blank=True)
    bare_body = RichTextUploadingField(
        blank=True, config_name='special')
    categories = models.ForeignKey(
        Categories, on_delete=models.CASCADE, related_name='sb_acts')
    cases = models.ForeignKey(Cases, on_delete=models.CASCADE,
                              related_name='sb_acts_cases', blank=True)

    def __str__(self):
        return self.title


class Chapter(models.Model):
    """
    Chapter Model
    """
    state_act = models.ForeignKey(
        StateBareAct, on_delete=models.CASCADE, related_name='sb_acts_chap', blank=True)
    central_act = models.ForeignKey(
        CentralBareAct, on_delete=models.CASCADE, related_name='cb_acts_chap', blank=True)
    number = models.CharField(max_length=100)
    title = models.TextField(blank=True)

    def __str__(self):
        return self.number


class Section(models.Model):
    """
    Section Model
    """
    number = models.IntegerField(default=0)
    state_act = models.ForeignKey(
        StateBareAct, on_delete=models.CASCADE, related_name='sb_acts_sec', blank=True)
    central_act = models.ForeignKey(
        CentralBareAct, on_delete=models.CASCADE, related_name='cb_acts_sec', blank=True)
    title = models.TextField(null=True, blank=True)
    body = RichTextUploadingField(blank=True, config_name='special')
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name='chapters', blank=True)
    cases = models.ForeignKey(Cases, on_delete=models.CASCADE,
                              related_name='section_cases', blank=True)
    citations = RichTextUploadingField(
        blank=True, null=True, config_name='special')

    def __str__(self):
        return self.title


class SubSection(models.Model):
    """
    Sub Section Model
    """
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='sections', blank=True)
    title = models.TextField(null=True, blank=True)
    body = RichTextUploadingField(blank=True, config_name='special')
    sitations = RichTextUploadingField(
        blank=True, config_name='special')

    def __str__(self):
        return self.title


class Order(models.Model):
    """
    Order Model
    """
    title = models.TextField(blank=True)
    body = RichTextUploadingField(blank=True, config_name='special')
    sitations = models.TextField(blank=True)
    category = models.ForeignKey(
        Categories, on_delete=models.CASCADE, related_name='order_category', blank=True)
    cases = models.ForeignKey(Cases, on_delete=models.CASCADE,
                              related_name='order_cases', blank=True)
    state_act = models.ForeignKey(
        StateBareAct, on_delete=models.CASCADE, related_name='sb_acts_order', blank=True)
    central_act = models.ForeignKey(
        CentralBareAct, on_delete=models.CASCADE, related_name='cb_acts_order', blank=True)

    def __str__(self):
        return self.title


class Notifications(models.Model):
    """
    Notifications Model
    """
    title = models.TextField(blank=True)
    body = RichTextUploadingField(blank=True, config_name='special')
    sitations = models.TextField(blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='noti_category', null=True, blank=True)
    cases = models.ForeignKey(Cases, on_delete=models.CASCADE, related_name='noti_cases', null=True, blank=True)
    state_act = models.ForeignKey(StateBareAct, on_delete=models.CASCADE, related_name='sb_acts_noti', null=True, blank=True)
    central_act = models.ForeignKey(CentralBareAct, on_delete=models.CASCADE, related_name='cb_acts_noti', null=True, blank=True)

    def __str__(self):
        return self.title
