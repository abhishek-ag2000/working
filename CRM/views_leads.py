from .models_leads import Lead
from .forms_leads import LeadForm
from .models import Tags
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.views.generic import (
    CreateView, UpdateView, DetailView, TemplateView, View,DeleteView)
from company.models import Organisation,Company
from bracketline.models import BracketlineUser
from django.urls import reverse

class LeadListView(LoginRequiredMixin, TemplateView):
    model = Lead
    context_object_name = "lead_obj"
    template_name = "lead/leads.html"

    def get_queryset(self):
        queryset = self.model.objects.all().exclude(status='converted')
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(assigned_to__in=[self.request.user]) |
                Q(created_by=self.request.user))

        if self.request.GET.get('tag', None):
            queryset = queryset.filter(tags__in = self.request.GET.getlist('tag'))

        request_post = self.request.POST
        if request_post:
            if request_post.get('name'):
                queryset = queryset.filter(
                    Q(first_name__icontains=request_post.get('name')) &
                    Q(last_name__icontains=request_post.get('name')))
            if request_post.get('city'):
                queryset = queryset.filter(
                    city__icontains=request_post.get('city'))
            if request_post.get('email'):
                queryset = queryset.filter(
                    email__icontains=request_post.get('email'))
            if request_post.get('status'):
                queryset = queryset.filter(status=request_post.get('status'))
            if request_post.get('tag'):
                queryset = queryset.filter(tags__in=request_post.getlist('tag'))
            if request_post.get('source'):
                queryset = queryset.filter(source=request_post.get('source'))
            if request_post.getlist('assigned_to'):
                queryset = queryset.filter(
                    assigned_to__id__in=request_post.getlist('assigned_to'))
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation

        context["lead_obj"] = Lead.objects.filter(company=organisation.id)
        open_leads = self.get_queryset().exclude(status='closed')
        close_leads = self.get_queryset().filter(status='closed')
        # LEAD_STATUS = self.get_queryset().filter(status='status')
        # context["status"] = LEAD_STATUS
        context["open_leads"] = open_leads
        context["close_leads"] = close_leads
        context["per_page"] = self.request.POST.get('per_page')
        # context["source"] = LEAD_SOURCE
        # context["users"] = User.objects.filter(
        #     is_active=True).order_by('email')
        context["assignedto_list"] = [
            int(i) for i in self.request.POST.getlist('assigned_to', []) if i]
        context["request_tags"] = self.request.POST.getlist('tag')

        search = True if (
            self.request.POST.get('name') or self.request.POST.get('city') or
            self.request.POST.get('email') or self.request.POST.get('tag') or
            self.request.POST.get('status') or
            self.request.POST.get('source') or
            self.request.POST.get('assigned_to')
        ) else False

        context["search"] = search

        tag_ids = list(set(self.get_queryset().values_list('tags', flat=True,)))
        context["tags"] = Tags.objects.filter(id__in=tag_ids)

        tab_status = 'Open'
        if self.request.POST.get('tab_status'):
            tab_status = self.request.POST.get('tab_status')
        context['tab_status'] = tab_status

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class CreateLeadView(CreateView):
    model = Lead
    form_class = LeadForm
    template_name = "Lead/create_leads.html"

    # def dispatch(self, request, *args, **kwargs):
    #     print('wwwwwwwwwwwwwwwwwwwwwwwwwwww')

    #     if self.request.user.is_superuser:
    #         self.BracketlineUser = settings.AUTH_USER_MODEL.objects.filter().order_by('email')
    #         print(self.users)
    #     else:
    #         self.BracketlineUser = settings.AUTH_USER_MODEL.objects.filter().order_by('email')
    #     return super(CreateLeadView, self).dispatch(
    #         request, *args, **kwargs)

    # def get_form_kwargs(self):
    #     kwargs = super(CreateLeadView, self).get_form_kwargs()
    #     if self.request.user.is_superuser:
    #         self.BracketlineUser = settings.AUTH_USER_MODEL.objects.filter(is_active=True).order_by('email')
    #         kwargs.update({"assigned_to": self.BracketlineUser})

    #     return kwargs

    def form_valid(self, form):
        print('form valid')
        c = Company.objects.get(pk=self.kwargs['organisation_pk'])
        form.instance.company = c

        lead_obj = form.save(commit=False)
        if self.request.POST.getlist('assigned_to', []):
            lead_obj.assigned_to.add(
                *self.request.POST.getlist('assigned_to'))
       
        if self.request.POST.getlist('teams', []):
            user_ids = Teams.objects.filter(id__in=self.request.POST.getlist('teams')).values_list('BracketlineUser', flat=True)
            assinged_to_users_ids = lead_obj.assigned_to.all().values_list('id', flat=True)
            for user_id in user_ids:
                if user_id not in assinged_to_users_ids:
                    lead_obj.assigned_to.add(user_id)

        assigned_to_list = list(lead_obj.assigned_to.all().values_list('id', flat=True))
        print('test asign list ................',assigned_to_list)


    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            
            lead_obj = form.save(commit=False)
            lead_obj.created_by = self.request.user
            c = Company.objects.get(pk=self.kwargs['organisation_pk'])
        
            lead_obj.company=c
            lead_obj.save()
            # if self.request.GET.get('view_account', None):
            #     if Account.objects.filter(
            #             id=int(self.request.GET.get('view_account'))).exists():
            #         Account.objects.get(id=int(self.request.GET.get(
            #             'view_account'))).contacts.add(lead_obj)
            return redirect('CRM:crm_leads',organisation_pk=self.kwargs['organisation_pk'])

        return self.form_invalid(form)


    

    def get_context_data(self, **kwargs):
        context = super(CreateLeadView, self).get_context_data(**kwargs)

        
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation

        context["lead_form"] = context["form"]
        
        # context["users"] = BracketlineUser
        context["assignedto_list"] = [
            int(i) for i in self.request.POST.getlist('assigned_to', []) if i]
      
        
        return context

class UpdateLeadView(UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = "Lead/create_leads.html"

    # def dispatch(self, request, *args, **kwargs):
    #     print('wwwwwwwwwwwwwwwwwwwwwwwwwwww')

    #     if self.request.user.is_superuser:
    #         self.BracketlineUser = settings.AUTH_USER_MODEL.objects.filter().order_by('email')
    #         print(self.users)
    #     else:
    #         self.BracketlineUser = settings.AUTH_USER_MODEL.objects.filter().order_by('email')
    #     return super(CreateLeadView, self).dispatch(
    #         request, *args, **kwargs)

    # def get_form_kwargs(self):
    #     kwargs = super(CreateLeadView, self).get_form_kwargs()
    #     if self.request.user.is_superuser:
    #         self.BracketlineUser = settings.AUTH_USER_MODEL.objects.filter(is_active=True).order_by('email')
    #         kwargs.update({"assigned_to": self.BracketlineUser})

    #     return kwargs
    def get_object(self):
            return get_object_or_404(Lead, pk=self.kwargs['lead_pk'])

    def get_success_url(self, **kwargs):
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        return reverse('CRM:crm_leads', kwargs={'organisation_pk': organisation.pk})

    def form_valid(self, form):
        print("befor save")
        c = Company.objects.get(pk=self.kwargs['organisation_pk'])
        form.instance.company = c
        form.instance.user = self.request.user
        
        return super(UpdateLeadView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
      
        form = self.get_form()
        if form.is_valid():
            lead_obj = form.save(commit=False)
            lead_obj.save()
            return self.form_valid(form)
        return self.form_invalid(form)

    # def form_valid(self, form):
    #     print('form valid')
    #     c = Company.objects.get(pk=self.kwargs['organisation_pk'])
    #     form.instance.company = c

    #     lead_obj = form.save(commit=False)
    #     if self.request.POST.getlist('assigned_to', []):
    #         lead_obj.assigned_to.add(
    #             *self.request.POST.getlist('assigned_to'))
       
    #     if self.request.POST.getlist('teams', []):
    #         user_ids = Teams.objects.filter(id__in=self.request.POST.getlist('teams')).values_list('BracketlineUser', flat=True)
    #         assinged_to_users_ids = lead_obj.assigned_to.all().values_list('id', flat=True)
    #         for user_id in user_ids:
    #             if user_id not in assinged_to_users_ids:
    #                 lead_obj.assigned_to.add(user_id)

    #     assigned_to_list = list(lead_obj.assigned_to.all().values_list('id', flat=True))
    #     print('test asign list ................',assigned_to_list)


    # def post(self, request, *args, **kwargs):
    #     self.object = None
    #     form = self.get_form()
    #     if form.is_valid():
            
    #         lead_obj = form.save(commit=False)
    #         lead_obj.created_by = self.request.user
    #         c = Company.objects.get(pk=self.kwargs['organisation_pk'])
        
    #         lead_obj.company=c
    #         lead_obj.save()
    #         # if self.request.GET.get('view_account', None):
    #         #     if Account.objects.filter(
    #         #             id=int(self.request.GET.get('view_account'))).exists():
    #         #         Account.objects.get(id=int(self.request.GET.get(
    #         #             'view_account'))).contacts.add(lead_obj)
    #         return redirect('CRM:crm_leads',organisation_pk=self.kwargs['organisation_pk'])

    #     return self.form_invalid(form)


    

    def get_context_data(self, **kwargs):
        context = super(UpdateLeadView, self).get_context_data(**kwargs)

        
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation

        context["lead_form"] = context["form"]
        
        # context["users"] = BracketlineUser
        context["assignedto_list"] = [
            int(i) for i in self.request.POST.getlist('assigned_to', []) if i]
      
        
        return context

class DetailLeadView(DetailView):
    model = Lead
    template_name = "lead/lead_detail.html"

    def get_object(self):
            return get_object_or_404(Lead, pk=self.kwargs['lead_pk'])


    def get_context_data(self, **kwargs):
        context = super(DetailLeadView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])

        context['organisation'] = organisation
        lead_details=get_object_or_404(
            Lead, pk=self.kwargs['lead_pk'])
        context['lead_details']=lead_details
        assigned_data = []
        for each in context['lead_details'].assigned_to.all():
            assigned_dict = {}
            assigned_dict['id'] = each.id
            assigned_dict['name'] = each.email
            assigned_data.append(assigned_dict)
        print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww',assigned_data)

        

        return context

# def create_lead(request):
#     template_name = "create_lead.html"
#     users = []
#     if request.user.is_superuser:
#         users = User.objects.filter(is_active=True).order_by('email')
#     elif request.user.google.all():
#         users = []
#     else:
#         users = User.objects.filter(role='ADMIN').order_by('email')
#     form = LeadForm(assigned_to=users)

#     if request.POST:
#         form = LeadForm(request.POST, request.FILES, assigned_to=users)
#         if form.is_valid():
#             lead_obj = form.save(commit=False)
#             lead_obj.created_by = request.user
#             lead_obj.save()
#             if request.POST.get('tags', ''):
#                 tags = request.POST.get("tags")
#                 splitted_tags = tags.split(",")
#                 for t in splitted_tags:
#                     tag = Tags.objects.filter(name=t)
#                     if tag:
#                         tag = tag[0]
#                     else:
#                         tag = Tags.objects.create(name=t)
#                     lead_obj.tags.add(tag)
#             if request.POST.getlist('assigned_to', []):
#                 lead_obj.assigned_to.add(*request.POST.getlist('assigned_to'))
#                 assigned_to_list = request.POST.getlist('assigned_to')
#                 # current_site = get_current_site(request)
#                 # recipients = assigned_to_list
#                 # send_email_to_assigned_user.delay(recipients, lead_obj.id, domain=current_site.domain,
#                 #     protocol=request.scheme)
#                 # for assigned_to_user in assigned_to_list:
#                 #     user = get_object_or_404(User, pk=assigned_to_user)
#                 #     mail_subject = 'Assigned to lead.'
#                 #     message = render_to_string(
#                 #         'assigned_to/leads_assigned.html', {
#                 #             'user': user,
#                 #             'domain': current_site.domain,
#                 #             'protocol': request.scheme,
#                 #             'lead': lead_obj
#                 #         })
#                 #     email = EmailMessage(
#                 #         mail_subject, message, to=[user.email])
#                 #     email.content_subtype = "html"
#                 #     email.send()
#             if request.POST.getlist('teams', []):
#                 user_ids = Teams.objects.filter(id__in=request.POST.getlist('teams')).values_list('users', flat=True)
#                 assinged_to_users_ids = lead_obj.assigned_to.all().values_list('id', flat=True)
#                 for user_id in user_ids:
#                     if user_id not in assinged_to_users_ids:
#                         lead_obj.assigned_to.add(user_id)

#             # current_site = get_current_site(request)
#             # recipients = list(lead_obj.assigned_to.all().values_list('id', flat=True))
#             # send_email_to_assigned_user.delay(recipients, lead_obj.id, domain=current_site.domain,
#             #     protocol=request.scheme)

#             # if request.FILES.get('lead_attachment'):
#             #     attachment = Attachments()
#             #     attachment.created_by = request.user
#             #     attachment.file_name = request.FILES.get(
#             #         'lead_attachment').name
#             #     attachment.lead = lead_obj
#             #     attachment.attachment = request.FILES.get('lead_attachment')
#             #     attachment.save()

#             if request.POST.get('status') == "converted":
#                 account_object = Account.objects.create(
#                     created_by=request.user, name=lead_obj.account_name,
#                     email=lead_obj.email, phone=lead_obj.phone,
#                     description=request.POST.get('description'),
#                     website=request.POST.get('website'),
#                 )
#                 account_object.billing_address_line = lead_obj.address_line
#                 account_object.billing_street = lead_obj.street
#                 account_object.billing_city = lead_obj.city
#                 account_object.billing_accounts_state = lead_obj.state
#                 account_object.billing_postcode = lead_obj.postcode
#                 account_object.billing_accounts_country = lead_obj.country
#                 for tag in lead_obj.tags.all():
#                     account_object.tags.add(tag)

#                 if request.POST.getlist('assigned_to', []):
#                     # account_object.assigned_to.add(*request.POST.getlist('assigned_to'))
#                     assigned_to_list = request.POST.getlist('assigned_to')
#                     current_site = get_current_site(request)
#                     recipients = assigned_to_list
#                     send_email_to_assigned_user.delay(recipients, lead_obj.id, domain=current_site.domain,
#                         protocol=request.scheme)
#                     # for assigned_to_user in assigned_to_list:
#                     #     user = get_object_or_404(User, pk=assigned_to_user)
#                     #     mail_subject = 'Assigned to account.'
#                     #     message = render_to_string(
#                     #         'assigned_to/account_assigned.html', {
#                     #             'user': user,
#                     #             'domain': current_site.domain,
#                     #             'protocol': request.scheme,
#                     #             'account': account_object
#                     #         })
#                     #     email = EmailMessage(
#                     #         mail_subject, message, to=[user.email])
#                     #     email.content_subtype = "html"
#                     #     email.send()

#                 account_object.save()
#             success_url = reverse('CRM:crm_leads')
#             # if request.POST.get("savenewform"):
#             #     success_url = reverse("leads:add_lead")
#             return JsonResponse({'error': False, 'success_url': success_url})
#         return JsonResponse({'error': True, 'errors': form.errors})
#     context = {}
#     context["lead_form"] = form
#     context["accounts"] = Account.objects.filter(status="open")
#     context["users"] = users
#     context["countries"] = COUNTRIES
#     context["status"] = LEAD_STATUS
#     context["source"] = LEAD_SOURCE
#     context["assignedto_list"] = [
#         int(i) for i in request.POST.getlist('assigned_to', []) if i]

#     return render(request, template_name, context)
