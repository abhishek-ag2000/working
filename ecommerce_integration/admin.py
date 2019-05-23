from django.contrib import admin
from ecommerce_integration.models import coupon, Product, Product_review, Services, API, Role_based_product
# Register your models here.

class productreviewdebit(admin.TabularInline):
	model = Product_review
	fk_name = 'reviews'


class productadmin(admin.ModelAdmin):
	model = Product
	list_display = ['id', 'title','price']
	search_fields = ['title','price']
	inlines = [
           productreviewdebit,
           ]

class rolebasedproductadmin(admin.ModelAdmin):
	model = Role_based_product
	list_display = ['id', 'title','price']
	search_fields = ['title','price']



admin.site.register(coupon)
admin.site.register(Product,productadmin)
admin.site.register(Product_review)
admin.site.register(Services)
admin.site.register(API)
admin.site.register(Role_based_product,rolebasedproductadmin)