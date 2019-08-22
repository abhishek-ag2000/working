from django.conf.urls import url
from qr_code import views, views_qrstock,views_employee

app_name = 'qr_code'

urlpatterns = [

    ########################### QR Dashboard ###############################################

    url(r'^company/(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/qr_dashboard/$',
        views.QRDashboard.as_view(), name='qr_dashboard'),


    ########################### QR-Stock Urls ###############################################

    url(r'^company/(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/stock_items_qr/$',
        views_qrstock.StocksForQRListView.as_view(), name='stock_items_qr'),

    url(r'^company/(?P<organisation_pk>\d+)/stock/(?P<qr_code_pk>\d+)/date/(?P<period_selected_pk>\d+)/stock_items_qr/$',
        views_qrstock.StockitemDetailsQRView.as_view(), name='stock_items_details_qr'),

    url(r'^company/(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/create_stock_items_qr/$',
        views_qrstock.StockMasterQRCreateview.as_view(), name='create_stock_items_qr'),

    url(r'^company/(?P<organisation_pk>\d+)/stock/(?P<qr_code_pk>\d+)/date/(?P<period_selected_pk>\d+)/update_stock_items_qr/$',
        views_qrstock.StockMasterQRUpdateView.as_view(), name='update_stock_items_qr'),

    url(r'^company/(?P<organisation_pk>\d+)/stock/(?P<qr_code_pk>\d+)/date/(?P<period_selected_pk>\d+)/generate_qr/$',
        views_qrstock.generate_qr_code, name='generate_qr_code'),

    url(r'^company/(?P<organisation_pk>\d+)/stock/(?P<qr_code_pk>\d+)/date/(?P<period_selected_pk>\d+)/download_qr/$',
        views_qrstock.download_qr_code, name='download_qr'),


    ########################### QR-Employee Urls ###############################################

    url(r'^company/(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/employee_qr/$',
        views_employee.EmployeeQrListView.as_view(), name='employee_qr'),

    url(r'^company/(?P<organisation_pk>\d+)/employee/(?P<qr_code_pk>\d+)/date/(?P<period_selected_pk>\d+)/employee_qr/$',
        views_employee.EmployeeQrDetailsQRView.as_view(), name='employee_details_qr'),

    url(r'^company/(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/register_employee_qr/$',
        views_employee.EmployeeMasterQRCreateview.as_view(), name='register_employee_qr'),

    url(r'^company/(?P<organisation_pk>\d+)/employee/(?P<qr_code_pk>\d+)/date/(?P<period_selected_pk>\d+)/update_employee_qr/$',
        views_employee.EmployeeMasterQRRUpdateView.as_view(), name='update_employee_qr'),

    url(r'^company/(?P<organisation_pk>\d+)/employee/(?P<qr_code_pk>\d+)/date/(?P<period_selected_pk>\d+)/generate_employee_qr/$',
        views_employee.generate_employee_qr_code, name='generate_employee_qr'),

]
