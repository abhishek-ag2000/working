import pytz
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  TemplateView, UpdateView, View)

from .models_accounts import Account, Email, Tags
# from accounts.tasks import send_email, send_email_to_assigned_user
# from cases.models import Case
# from common.access_decorators_mixins import (MarketingAccessRequiredMixin,
#                                              SalesAccessRequiredMixin,
#                                              marketing_access_required,
#                                              sales_access_required)
from bracketline.models import BracketlineUser
# from common.tasks import send_email_user_mentions
# from common.utils import (CASE_TYPE, COUNTRIES, CURRENCY_CODES, INDCHOICES,
#                           PRIORITY_CHOICE, STATUS_CHOICE)
from .models_contacts import Contact
# from .models_leads import Lead
# from .models_opportunity import SOURCES, STAGES, Opportunity
from .models_teams import Teams
from django.contrib.auth.models import (AbstractBaseUser)
from company.models import Organisation,Company
from .forms_accounts import AccountForm


class AccountsListView(LoginRequiredMixin, TemplateView):
    model = Account
    context_object_name = "accounts_list"
    template_name = "accounts/accounts.html"

    def get_queryset(self):
        queryset = self.model.objects.all()
        # if self.request.user.role != "ADMIN" and not self.request.user.is_superuser:
        #     queryset = queryset.filter(
        #         Q(created_by=self.request.user) | Q(assigned_to=self.request.user)).distinct()

        # if self.request.GET.get('tag', None):
        #     queryset = queryset.filter(tags__in = self.request.GET.getlist('tag'))

        request_post = self.request.POST
        if request_post:
            if request_post.get('name'):
                queryset = queryset.filter(
                    name__icontains=request_post.get('name'))
            if request_post.get('city'):
                queryset = queryset.filter(
                    billing_city__contains=request_post.get('city'))
            if request_post.get('industry'):
                queryset = queryset.filter(
                    industry__icontains=request_post.get('industry'))
            if request_post.get('tag'):
                queryset = queryset.filter(tags__in=request_post.getlist('tag'))

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super(AccountsListView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation

      
        open_accounts = self.get_queryset().filter(status='open')
        close_accounts = self.get_queryset().filter(status='close')
        context["accounts_list"] = Account.objects.filter(company=organisation.id)
        # context["users"] = User.objects.filter(
        #     is_active=True).order_by('email')
        context['open_accounts'] = open_accounts
        context['close_accounts'] = close_accounts
       
        context["per_page"] = self.request.POST.get('per_page')
        tag_ids = list(set(Account.objects.values_list('tags', flat=True)))
        context["tags"] = Tags.objects.filter(id__in=tag_ids)
        if self.request.POST.get('tag', None):
            context["request_tags"] = self.request.POST.getlist('tag')
        elif self.request.GET.get('tag', None):
            context["request_tags"] = self.request.GET.getlist('tag')
        else:
            context["request_tags"] = None

        search = False
        if (
            self.request.POST.get('name') or self.request.POST.get('city') or
            self.request.POST.get('industry') or self.request.POST.get('tag')
        ):
            search = True

        context["search"] = search

        tab_status = 'Open'
        if self.request.POST.get('tab_status'):
            tab_status = self.request.POST.get('tab_status')
        context['tab_status'] = tab_status
        TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]
        context["timezones"] = TIMEZONE_CHOICES
        context["settings_timezone"] = settings.TIME_ZONE

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class CreateAccountView( LoginRequiredMixin, CreateView):
    model = Account
    form_class = AccountForm
    template_name = "accounts/create_account.html"

    # def dispatch(self, request, *args, **kwargs):
    #     if self.request.user.is_superuser:
    #         self.users = User.objects.filter(is_active=True).order_by('email')
    #     elif request.user.google.all():
    #         self.users = []
    #     else:
    #         self.users = User.objects.filter(role='ADMIN').order_by('email')
    #     return super(
    #         CreateAccountView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateAccountView, self).get_form_kwargs()
        kwargs.update({"account": True})
        kwargs.update({"request_user": self.request.user})
        # if self.request.user.role != "ADMIN" and not self.request.user.is_superuser:
        #     kwargs.update({"request_user": self.request.user})
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        # Save Account
        account_object = form.save(commit=False)
        account_object.created_by = self.request.user
        c = Company.objects.get(pk=self.kwargs['organisation_pk'])
        
        account_object.company=c
        account_object.save()

        if self.request.POST.get('tags', ''):
            tags = self.request.POST.get("tags")
            splitted_tags = tags.split(",")
            for t in splitted_tags:
                tag = Tags.objects.filter(name=t.lower())
                if tag:
                    tag = tag[0]
                else:
                    tag = Tags.objects.create(name=t.lower())
                account_object.tags.add(tag)
        if self.request.POST.getlist('contacts', []):
            account_object.contacts.add(*self.request.POST.getlist('contacts'))
        if self.request.POST.getlist('assigned_to', []):
            account_object.assigned_to.add(*self.request.POST.getlist('assigned_to'))
        # if self.request.FILES.get('account_attachment'):
        #     attachment = Attachments()
        #     attachment.created_by = self.request.user
        #     attachment.file_name = self.request.FILES.get(
        #         'account_attachment').name
        #     attachment.account = account_object
        #     attachment.attachment = self.request.FILES.get(
        #         'account_attachment')
        #     attachment.save()
        if self.request.POST.getlist('teams', []):
            user_ids = Teams.objects.filter(id__in=self.request.POST.getlist('teams')).values_list('users', flat=True)
            assinged_to_users_ids = account_object.assigned_to.all().values_list('id', flat=True)
            for user_id in user_ids:
                if user_id not in assinged_to_users_ids:
                    account_object.assigned_to.add(user_id)

        assigned_to_list = list(account_object.assigned_to.all().values_list('id', flat=True))
        print('------------------------------------------------',assigned_to_list)
        # current_site = get_current_site(self.request)
        # recipients = assigned_to_list
        # send_email_to_assigned_user.delay(recipients, account_object.id, domain=current_site.domain,
        #     protocol=self.request.scheme)

        # if self.request.POST.get("savenewform"):
        #     return redirect("accounts:new_account")

        # if self.request.is_ajax():
        #     data = {'success_url': reverse_lazy(
        #         'accounts:list'), 'error': False}
        #     return JsonResponse(data)

        return redirect("CRM:crm_accounts", organisation_pk=self.kwargs['organisation_pk'])

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse({'error': True, 'errors': form.errors})
        return self.render_to_response(
            self.get_context_data(form=form)
        )

    def get_context_data(self, **kwargs):
        context = super(CreateAccountView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation

        context["account_form"] = context["form"]
      
       
        
        # context["contact_count"] = Contact.objects.count()
        if self.request.user.is_superuser:
            # context["leads"] = Lead.objects.exclude(
            #     status__in=['converted', 'closed'])
            context["contacts"] = Contact.objects.all()
        # else:
            # context["leads"] = Lead.objects.filter(
            #     Q(assigned_to__in=[self.request.user]) | Q(created_by=self.request.user)).exclude(
        #     #     status__in=['converted', 'closed'])
        # context["lead_count"] = context["leads"].count()
        if not self.request.user.is_superuser:
            # context["lead_count"] = Lead.objects.filter(
            #     Q(assigned_to__in=[self.request.user]) | Q(created_by=self.request.user)).exclude(status='closed').count()
            context["contacts"] = Contact.objects.filter(
                Q(assigned_to__in=[self.request.user]) | Q(created_by=self.request.user))
        context["contact_count"] = context["contacts"].count()
        return context


class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account
    context_object_name = "account_details"
    template_name = "accounts/account_detail.html"

    def get_object(self):
            return get_object_or_404(Account, pk=self.kwargs['account_pk'])

    def get_context_data(self, **kwargs):
        context = super(AccountDetailView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])

        context['organisation'] = organisation
        account_details=get_object_or_404(
            Account, pk=self.kwargs['account_pk'])
     
        account_details = context["account_details"]
        if not self.request.user.is_superuser:
            if not ((self.request.user == account_details.created_by) or
                (self.request.user in account_details.assigned_to.all())):
                raise PermissionDenied

        comment_permission = True if (
            self.request.user == account_details.created_by or
            self.request.user.is_superuser 
        ) else False

        # if self.request.user.is_superuser:
        #     users_mention = list(User.objects.filter(is_active=True).values('username'))
        # elif self.request.user != account_details.created_by:
        #     if account_details.created_by:
        #         users_mention = [{'username': account_details.created_by.username}]
        #     else:
        #         users_mention = []
        # else:
        #     users_mention = []

        context.update({
            # "comments": account_details.accounts_comments.all(),
            # "attachments": account_details.account_attachment.all(),
            # "opportunity_list": Opportunity.objects.filter(
            #     account=account_details),
            "contacts": account_details.contacts.all(),
            # "users": User.objects.filter(is_active=True).order_by('email'),
            # "cases": Case.objects.filter(account=account_details),
            # "stages": STAGES,
            # "sources": SOURCES,
            # "countries": COUNTRIES,
            # "currencies": CURRENCY_CODES,
            # "case_types": CASE_TYPE,
            # "case_priority": PRIORITY_CHOICE,
            # "case_status": STATUS_CHOICE,
            # 'comment_permission': comment_permission,
            # 'tasks':account_details.accounts_tasks.all(),
            # 'invoices':account_details.accounts_invoices.all(),
            # 'emails':account_details.sent_email.all(),
            # 'users_mention': users_mention,
        })
        return context


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = "accounts/create_account.html"

    def get_object(self):
            return get_object_or_404(Account, pk=self.kwargs['account_pk'])
  
    def get_success_url(self, **kwargs):
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        return reverse('CRM:crm_accounts', kwargs={'organisation_pk': organisation.pk})

    def form_valid(self, form):
        print("befor save")
        c = Company.objects.get(pk=self.kwargs['organisation_pk'])
        form.instance.company = c
        form.instance.user = self.request.user
        print(form.instance.user)
        return super(AccountUpdateView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
      
        form = self.get_form()
        
        if form.is_valid():
            
            contact_obj = form.save(commit=False)

            return self.form_valid(form)
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(AccountUpdateView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation

        context["account_form"] = context["form"]
      
       
        
        # context["contact_count"] = Contact.objects.count()
        if self.request.user.is_superuser:
            # context["leads"] = Lead.objects.exclude(
            #     status__in=['converted', 'closed'])
            context["contacts"] = Contact.objects.all()
            print('superuser contact')
            
        # else:
            # context["leads"] = Lead.objects.filter(
            #     Q(assigned_to__in=[self.request.user]) | Q(created_by=self.request.user)).exclude(
        #     #     status__in=['converted', 'closed'])
        # context["lead_count"] = context["leads"].count()
        if not self.request.user.is_superuser:
            # context["lead_count"] = Lead.objects.filter(
            #     Q(assigned_to__in=[self.request.user]) | Q(created_by=self.request.user)).exclude(status='closed').count()
            context["contacts"] = Contact.objects.filter(
                Q(assigned_to__in=[self.request.user]) | Q(created_by=self.request.user))
            print('normal contact')
        context["contact_count"] = context["contacts"].count()
        return context

# def account_delete_ajax(request, account_pk):
#     data = {'is_error': False, 'error_message': ""}

#     # data['is_error'] = True
#     # data['error_message'] = "Not allowed!"
#     # return JsonResponse(data)

#     organisation = Organisation.objects.filter(pk=organisation_pk).first()
#     if not organisation:
#         data['is_error'] = True
#         data['error_message'] = "No Company found with the ID supplied"
#         return JsonResponse(data)

#     if request.method == "POST":
#         try:
#             organisation.delete()
#         except IntegrityError:
#             data['is_error'] = True
#             data['error_message'] = "Cannot delete the company it has reference!"
#             return JsonResponse(data)

#         period_selected = PeriodSelected.objects.filter(
#             user=request.user).first()
#         if not period_selected:
#             data['is_error'] = True
#             data['error_message'] = "Period selection information unavailable; please refresh page"
#             return JsonResponse(data)

#         context = {
#             'organisation_list': Organisation.objects.filter(user=request.user).order_by('name'),
#             'period_selected': period_selected,
#             'Products': ProductActivated.objects.filter(user=request.user, product__id=1, is_active=True),
#             'Products_QR': ProductActivated.objects.filter(user=request.user, product__id=3, is_active=True),
#         }
#         data['organisation_list'] = render_to_string(
#             'organisation/organisation_list_2.html', context)
#     else:
#         context = {'organisation': organisation}
#         data['html_form'] = render_to_string(
#             'organisation/organisation_confirm_delete.html', context, request=request)

#     return JsonResponse(data)
