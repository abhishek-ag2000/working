"""
Admin
"""
from django.contrib import admin
from ecommerce_integration.models import Coupon, Product, ProductReview, Services, API, RoleBasedProduct


class ProductReviewAdmin(admin.TabularInline):
    """
    Tabular Inline admin class for product review model
    """
    model = ProductReview
    fk_name = 'reviews'


class ProductAdmin(admin.ModelAdmin):
    """
    Model Admin class for the product model
    """
    model = Product
    list_display = ['id', 'title', 'price']
    search_fields = ['title', 'price']
    inlines = [
        ProductReviewAdmin,
    ]


class RoleBasedProductAdmin(admin.ModelAdmin):
    """
    Model Admin Class for The RoleBasedProduct Model
    """
    model = RoleBasedProduct
    list_display = ['id', 'title', 'price']
    search_fields = ['title', 'price']


admin.site.register(Coupon)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductReview)
admin.site.register(Services)
admin.site.register(API)
admin.site.register(RoleBasedProduct, RoleBasedProductAdmin)
