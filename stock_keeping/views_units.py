"""
Views for Simple and Compound Units
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.functions import Coalesce
from django.db.models import Value, Count
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from company.models import Company
from user_profile.models import Profile
from messaging.models import Message

from accounting_entry.models import PeriodSelected
from accounting_entry.mixins import ProductExistsRequiredMixin
from .mixins import CompanyAccountsWithInventoryMixin
from .models import SimpleUnit, CompoundUnit
from .forms import SimpleUnitsForm, CompoundUnitForm


class SimpleUnitListView(ProductExistsRequiredMixin,  LoginRequiredMixin, ListView):
    """
    Simple Unit List View
    """
    context_object_name = 'simpleunits_list'
    model = SimpleUnit
    template_name = 'stock_keeping/simpleunits/simpleunits_list.html'
    paginate_by = 15

    def get_queryset(self):
        return self.model.objects.filter(company=self.kwargs['company_pk'])

    def get_context_data(self, **kwargs):
        context = super(SimpleUnitListView, self).get_context_data(**kwargs)
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class SimpleUnitDetailView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Simple Unit Details View
    """
    context_object_name = 'simpleunits_details'
    model = SimpleUnit
    template_name = 'stock_keeping/simpleunits/simpleunits_details.html'

    def get_object(self):
        return get_object_or_404(SimpleUnit, pk=self.kwargs['simpleunit_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        simple_unit = self.get_object()
        return self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user == simple_unit.user

    def get_context_data(self, **kwargs):
        context = super(SimpleUnitDetailView, self).get_context_data(**kwargs)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class SimpleUnitCreateView(ProductExistsRequiredMixin,  LoginRequiredMixin, CreateView):
    """
    Simple Unit Create View
    """
    form_class = SimpleUnitsForm
    template_name = "stock_keeping/simpleunits/SimpleUnitsForm.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:simplelist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = SimpleUnit.objects.filter(user=self.request.user, company=company).count() + 1
        form.instance.counter = counter
        return super(SimpleUnitCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(SimpleUnitCreateView, self).get_context_data(**kwargs)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class SimpleUnitUpdateView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Simple Unit Update View
    """
    model = SimpleUnit
    form_class = SimpleUnitsForm
    template_name = "stock_keeping/simpleunits/SimpleUnitsForm.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        simpleunits_details = get_object_or_404(SimpleUnit, pk=self.kwargs['simpleunit_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:simpledetail', kwargs={'company_pk': company.pk, 'simpleunit_pk': simpleunits_details.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(SimpleUnit, pk=self.kwargs['simpleunit_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        simpleunits = self.get_object()
        return self.request.user in company.accountant.all() or self.request.user == simpleunits.user

    def get_context_data(self, **kwargs):
        context = super(SimpleUnitUpdateView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class SimpleUnitDeleteView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Simple Unit Delete View
    """
    model = SimpleUnit
    template_name = "stock_keeping/simpleunits/simpleunits_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:simplelist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(SimpleUnit, pk=self.kwargs['simpleunit_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        receipts = self.get_object()
        return self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user == receipts.user

    def get_context_data(self, **kwargs):
        context = super(SimpleUnitDeleteView, self).get_context_data(**kwargs)
        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


##################################### Compound Unit Views #####################################


class CompoundUnitListView(ProductExistsRequiredMixin,  LoginRequiredMixin, ListView):
    """
    Compound Unit List View
    """
    context_object_name = 'compoundunits_list'
    model = CompoundUnit
    template_name = 'stock_keeping/compoundunits/compoundunits_list.html'
    paginate_by = 15

    def get_queryset(self):
        return self.model.objects.filter(company=self.kwargs['company_pk'])

    def get_context_data(self, **kwargs):
        context = super(CompoundUnitListView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class CompoundUnitDetailView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DetailView):
    """
    Compound Unit Details View
    """
    context_object_name = 'compoundunits_details'
    model = CompoundUnit
    template_name = 'stock_keeping/compoundunits/compoundunits_details.html'

    def get_object(self):
        return get_object_or_404(CompoundUnit, pk=self.kwargs['compound_unit_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        compounds = self.get_object()
        return self.request.user in company.auditor.all() or self.request.user in company.accountant.all() or self.request.user == compounds.user

    def get_context_data(self, **kwargs):
        context = super(CompoundUnitDetailView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class CompoundUnitCreateView(ProductExistsRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Compound Unit Create View
    """
    form_class = CompoundUnitForm
    template_name = "stock_keeping/compoundunits/CompoundUnitForm.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:compoundlist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        form.instance.company = company
        counter = CompoundUnit.objects.filter(user=self.request.user, company=company).count() + 1
        form.instance.counter = counter
        return super(CompoundUnitCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        data = super(CompoundUnitCreateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(CompoundUnitCreateView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class CompoundUnitUpdateView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Compound Unit Update View
    """
    model = CompoundUnit
    form_class = CompoundUnitForm
    template_name = "stock_keeping/compoundunits/CompoundUnitForm.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        compoundunits_details = get_object_or_404(CompoundUnit, pk=self.kwargs['compound_unit_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:compounddetail', kwargs={'company_pk': company.pk, 'compound_unit_pk': compoundunits_details.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(CompoundUnit, pk=self.kwargs['compound_unit_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        compounds = self.get_object()
        return self.request.user in company.accountant.all() or self.request.user == compounds.user

    def get_form_kwargs(self):
        data = super(CompoundUnitUpdateView, self).get_form_kwargs()
        data.update(
            user=self.request.user,
            company=Company.objects.get(pk=self.kwargs['company_pk'])
        )
        return data

    def get_context_data(self, **kwargs):
        context = super(CompoundUnitUpdateView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context


class CompoundUnitDeleteView(ProductExistsRequiredMixin,  UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    """
    Compound Unit Delete View
    """
    model = CompoundUnit
    template_name = "stock_keeping/compoundunits/compoundunits_confirm_delete.html"

    def get_success_url(self, **kwargs):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        return reverse('stock_keeping:compoundlist', kwargs={'company_pk': company.pk, 'period_selected_pk': period_selected.pk})

    def get_object(self):
        return get_object_or_404(CompoundUnit, pk=self.kwargs['compound_unit_pk'])

    def test_func(self):
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        compounds = self.get_object()
        return self.request.user in company.accountant.all() or self.request.user == compounds.user

    def get_context_data(self, **kwargs):
        context = super(CompoundUnitDeleteView, self).get_context_data(**kwargs)

        context['profile_details'] = Profile.objects.all()
        company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        context['company'] = company
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        context['inbox'] = Message.objects.filter(reciever=self.request.user)
        context['inbox_count'] = context['inbox'].aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']
        context['send_count'] = Message.objects.filter(sender=self.request.user).aggregate(the_sum=Coalesce(Count('id'), Value(0)))['the_sum']

        return context
