"""
View
"""
import calendar
import collections
import dateutil
from django.db.models import Case, When, Value, Sum, Count, F
from django.db.models.functions import Coalesce
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, TemplateView
from blog.models import Blog
from consultancy.models import Consultancy
from company.models import Company
from accounting_entry.models import PeriodSelected
from stock_keeping.models_sale import SaleVoucher
from stock_keeping.models_purchase import PurchaseVoucher
from user_profile.models import Profile, ProductActivated, RoleBasedProductActivated
from ecommerce_integration.models import Product, Services, API
from messaging.models import Message


class HomePage(ListView):
    """
    Home Page View
    """
    template_name = "clouderp/landing.html"

    def get_queryset(self):
        return Blog.objects.all().annotate(num_submissions=Count('likes')).order_by('-num_submissions')[:4]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("ecommerce_integration:productlist"))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context['total_consultancies'] = Consultancy.objects.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['bussiness_user_count'] = Profile.objects.filter(user_type__icontains='Bussiness User').aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['professional_user_count'] = Profile.objects.filter(user_type__icontains='Professional').aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['data_operator_count'] = Profile.objects.filter(user_type__icontains='Data Operators').aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['Products'] = Product.objects.all()
        context['services_list'] = Services.objects.all()
        context['api_list'] = API.objects.all()
        context['product_count'] = Product.objects.aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['users'] = Profile.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        return context


class BaseView1(TemplateView):
    """
    Base View 1
    """
    template_name = "clouderp/base.html"

    def get_context_data(self, **kwargs):
        context = super(BaseView1, self).get_context_data(**kwargs)

        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, id=1, is_active=True)
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        results = collections.OrderedDict()
        result = SaleVoucher.objects.filter(user=self.request.user, company=company, voucher_date__gte=period_selected.start_date,
                                            date__lt=period_selected.end_date).annotate(real_total=Case(When(Total_Amount__isnull=True, then=0), default=F('Total_Amount')))
        result_purchase = PurchaseVoucher.objects.filter(user=self.request.user, company=company, voucher_date__gte=period_selected.start_date,
                                                         date__lt=period_selected.end_date).annotate(real_total_purchase=Case(When(Total_Purchase__isnull=True, then=0), default=F('Total_Purchase')))
        date_cursor = period_selected.start_date

        while date_cursor <= period_selected.end_date:
            month_partial_total = result.filter(date__month=date_cursor.month).aggregate(partial_total=Sum('real_total'))['partial_total']
            month_partial_total_purchase = result_purchase.filter(date__month=date_cursor.month).aggregate(partial_total_purchase=Sum('real_total_purchase'))['partial_total_purchase']

            if not month_partial_total:

                month_partial_total = int(0)
                e = month_partial_total

            else:

                e = month_partial_total

            if not month_partial_total_purchase:

                month_partial_total_purchase = int(0)
                z = month_partial_total_purchase

            else:

                z = month_partial_total_purchase

            results[calendar.month_name[date_cursor.month]] = [e, z]

            date_cursor += dateutil.relativedelta.relativedelta(months=1)

        context['data'] = results.items()
        return context


class BaseView2(TemplateView):
    """
    Base View 2
    """
    template_name = "clouderp/base_2.html"

    def get_context_data(self, **kwargs):
        context = super(BaseView2, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['active_product_1'] = ProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(user=self.request.user, product__id=1, is_active=True)
            context['inbox'] = Message.objects.filter(reciever=self.request.user)
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(user=self.request.user, product__id=10, is_active=True)
        else:
            context['active_product_1'] = ProductActivated.objects.filter(product__id=1, is_active=True)
            context['role_product_1'] = RoleBasedProductActivated.objects.filter(product__id=1, is_active=True)
            context['inbox'] = Message.objects.all()
            context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['send_count'] = Message.objects.all().aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
            context['product_legal'] = ProductActivated.objects.filter(product__id=10, is_active=True)
        return context
