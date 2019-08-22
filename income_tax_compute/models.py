"""
Income Tax Computation Models
"""
import datetime
from django.conf import settings
from django.db import models
from company.models import Company


def get_default_assesment_year():
    """
    Returns the default assesment year based on system date
    """
    # return str(datetime.datetime.now().year-1)+"-"+str(datetime.datetime.now().year) #assesment
    # financial
    return str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().year+1)


def get_choice_assesment_year():
    """
    Returns a tuple of assesment years based on system date
    """
    assesment_years = (
        (str(datetime.datetime.now().year-4)+"-"+str(datetime.datetime.now().year-3),
         str(datetime.datetime.now().year-4)+"-"+str(datetime.datetime.now().year-3)),
        (str(datetime.datetime.now().year-3)+"-"+str(datetime.datetime.now().year-2),
         str(datetime.datetime.now().year-3)+"-"+str(datetime.datetime.now().year-2)),
        (str(datetime.datetime.now().year-2)+"-"+str(datetime.datetime.now().year-1),
         str(datetime.datetime.now().year-2)+"-"+str(datetime.datetime.now().year-1)),
        (str(datetime.datetime.now().year-1)+"-"+str(datetime.datetime.now().year),
         str(datetime.datetime.now().year-1)+"-"+str(datetime.datetime.now().year)),
        (str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().year+1),
         str(datetime.datetime.now().year)+"-"+str(datetime.datetime.now().year+1))
    )
    return assesment_years


class IncomeTax(models.Model):
    """
    Income Tax model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='income_tax_user')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='income_tax_company')
    assesment_year = models.CharField(max_length=9, choices=get_choice_assesment_year(), default=get_default_assesment_year, null=False, blank=False)
    salary = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    salary_allowence = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    salary_taxable_perqisite = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    salary_gross = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    salary_deduction_us16 = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    salary_prof_tax = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    salary_entmnt_allowance = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    salary_total = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    house_property_net_adjusted = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    house_property_deduction_us24 = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    house_property_total = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    profit_gain_net_profit = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    profit_gain_income_not_allowable = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    profit_gain_expense_not_allowable = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    profit_gain_income_exempt = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    profit_gain_income_skiped = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    profit_gain_total = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    capital_gain_net = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    capital_gain_exempt = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    capital_gain_total = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    other_income_gross = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    other_income_deduction_us57 = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    other_income_total = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    total_income_1_2_3_4_5 = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    adjustment_setoff_loss = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    gross_total_income = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    deduction_80c_80u = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    net_income = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    tax_on_net_income = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    rebate = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    balance = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    surcharge = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    tax_and_surcharge = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    education_cess = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    tds = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    advance_tax = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    self_assessment_tax = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    prepaid_taxes = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)
    tax_liability_refund = models.DecimalField(default=0.00, max_digits=20, decimal_places=2)

    def __str__(self):
        return self.assesment_year
