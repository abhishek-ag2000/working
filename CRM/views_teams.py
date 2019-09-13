from .models_teams import Teams
from .forms_teams import TeamForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView, UpdateView, DetailView, TemplateView, View,DeleteView)
from company.models import Organisation,Company



class TeamListView( LoginRequiredMixin, TemplateView): # SalesAccessRequiredMixin
    
    model = Teams
    context_object_name = "team_obj_list"
    template_name = "team/teams.html"
    




    def get_context_data(self, **kwargs):
        
        context = super(TeamListView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation
        # print(organisation)


        context["team_obj_list"] = Teams.objects.filter(company=organisation.id)

        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class CreateTeamView(CreateView):
    model = Teams
    form_class = TeamForm
    template_name = "team/create_team.html"



    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            
            team_obj = form.save(commit=False)
            
            team_obj.created_by = self.request.user
            c = Company.objects.get(pk=self.kwargs['organisation_pk'])
        
            team_obj.company=c
            team_obj.save()

        return self.form_invalid(form)


    def get_success_url(self, **kwargs):
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        return reverse('CRM:crm_contacts', kwargs={'organisation_pk': organisation.pk})

    def form_valid(self, form):
        print("befor save")
        c = Company.objects.get(pk=self.kwargs['organisation_pk'])
        form.instance.company = c
        form.instance.created_by = self.request.user
        
        
        return super(CreateTeamView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        context = super(CreateTeamView, self).get_context_data(**kwargs)

        
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation

        context["team_form"] = context["form"]
     
        return context

class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Teams
    context_object_name = "team_details"
    template_name = "team/team_details.html"

    def get_object(self):
        return get_object_or_404(Teams, pk=self.kwargs['team_pk'])

    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(
            Organisation, pk=self.kwargs['organisation_pk'])

        context['organisation'] = organisation
        team_details=get_object_or_404(
            Teams, pk=self.kwargs['team_pk'])
     
        team_details = context["team_details"]
        if not self.request.user.is_superuser:

            raise PermissionDenied
 
        return context