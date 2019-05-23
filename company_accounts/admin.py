from django.contrib import admin
from company_accounts.models import Purchase_accounts,Sales_accounts,Purchase_Total,Sales_total
# Register your models here.

class Purchase_Totalinline(admin.TabularInline):
	model = Purchase_Total

class Sales_totalinline(admin.TabularInline):
	model = Sales_total

class Purchaseadmin(admin.ModelAdmin):
	model = Purchase_accounts
	list_display = ['User', 'Company','ref_no','Party_ac','purchase','sub_total']
	search_fields = ['User','Company','Party_ac','purchase','urlhash']
	inlines = [Purchase_Totalinline]

class Salesadmin(admin.ModelAdmin):
	model = Sales_accounts
	list_display = ['User', 'Company','ref_no','Party_ac','sales','sub_total']
	search_fields = ['User','Company','Party_ac','purchase','urlhash']
	inlines = [Sales_totalinline]


admin.site.register(Purchase_accounts, Purchaseadmin)
admin.site.register(Sales_accounts, Salesadmin)
admin.site.register(Purchase_Total)
admin.site.register(Sales_total)





