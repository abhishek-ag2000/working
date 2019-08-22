from django.contrib import admin
from .models import EmployeeMasterQR, StockMasterQR
# Register your models here.

# comment here
class EmployeeAdmin(admin.ModelAdmin):
    """
    Model Admin class for EmployeeMasterQR model
    """
    model = EmployeeMasterQR
    list_display = ['company', 'employee_name', 'url_hash']
    search_fields = ['employee_name', 'url_hash']


class StockAdmin(admin.ModelAdmin):
    """
    Model Admin class for StockMasterQR model
    """
    model = StockMasterQR
    list_display = ['company', 'stock_name', 'url_hash']
    search_fields = ['url_hash', 'stock_name']


admin.site.register(EmployeeMasterQR, EmployeeAdmin)
admin.site.register(StockMasterQR, StockAdmin)
