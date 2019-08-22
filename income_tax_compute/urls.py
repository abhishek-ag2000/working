'''
Income Tax Computation URLS
'''
from django.conf.urls import url
from income_tax_compute import views

app_name = 'income_tax_compute'

urlpatterns = [
    url(r'^company/(?P<company_pk>\d+)/incometax/date/(?P<period_selected_pk>\d+)/(?P<period>[0-9]{4}-[0-9]{4})/$',
        views.income_tax_detail_view, name='incometaxdetailview'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/incometaxupdate/(?P<instance_id>\d+)/field/(?P<field>[\w\-]+)/$',
        views.income_tax_value_update, name='IncomeTaxValueUpdate'),
    url(r'^ajax/ledger_value/$', views.get_ledger_value, name='get_ledger_value'),
    url(r'^company/(?P<company_pk>\d+)/date/(?P<period_selected_pk>\d+)/incometaxyearupdate/(?P<last_period>[0-9]{4}-[0-9]{4})/$',
        views.income_tax_year_update, name='IncomeTaxYearUpdate'),
]
