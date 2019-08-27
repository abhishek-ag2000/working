"""
URLs
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    url(r"^$", views.HomePage.as_view(), name="home"),
    url(r"^base/$", views.BaseView1.as_view(), name="base"),
    path('admin/', admin.site.urls),
    url(r"^bracketline/", include("bracketline.urls", namespace="bracketline")),
    url(r"^message/", include("messaging.urls", namespace="messaging")),
    #url(r"^accounts/", include("accounts.urls", namespace="accounts")),
    url(r"^accounts/", include("django.contrib.auth.urls")),
    url(r'^auth/', include('social_django.urls', namespace='social')),
    url(r"^products/", include("ecommerce_integration.urls", namespace="products")),
    url(r"^carts/", include("ecommerce_cart.urls", namespace="carts")),
    url(r"^accounting_entry/", include("accounting_entry.urls", namespace="accounting_entry")),
    url(r"^company/", include("company.urls", namespace="company")),
    url(r"^profile/", include("user_profile.urls", namespace="user_profile")),
    url(r"^blog/", include("blog.urls", namespace="blog")),
    url(r"^pdf/", include("pdf_report.urls", namespace="pdf")),
    url(r"^gst/", include("gst_reports.urls", namespace="gst")),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    url(r"^qr_code/", include("qr_code.urls", namespace="qr_code")),
    url(r"^consultancy/", include("consultancy.urls", namespace="consultancy")),
    url(r"^stock_keeping/", include("stock_keeping.urls", namespace="stock_keeping")),
    url(r"^aggrement/", include("aggrement.urls", namespace="aggrement")),
    url(r"^legal/", include("legal_database.urls", namespace="legal")),
    url(r"^helpsupport/", include("help_support.urls", namespace="help_support")),
    url(r"^income_tax_compute/", include("income_tax_compute.urls", namespace="income_tax_compute")),
    url(r'^ratings/', include('star_ratings.urls', namespace='ratings')),
    url(r'^job/', include('job.urls', namespace='job')),
    url(r'^CRM/', include('CRM.urls', namespace='CRM')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         url(r'^__debug__/',include(debug_toolbar.urls))
#     ] + urlpatterns
