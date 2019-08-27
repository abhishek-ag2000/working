from django.db import models

# from . import models_contacts
# from . import models_accounts
# from . import models_leads
# from . import models_opportunity
# from . import models_cases
# Create your models here.


class Tags(models.Model):
    name = models.CharField(max_length=20)
    slug = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Tags, self).save(*args, **kwargs)