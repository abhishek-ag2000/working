from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView
from .models import Resume, Job
from .forms import ResumeForm, JobPostForm
from company.models import Organisation
from accounting_entry.models import PeriodSelected
from django.shortcuts import get_object_or_404
from django.urls import reverse

# Create your views here.


class ResumeBuildView(CreateView):

    form_class = ResumeForm
    template_name = "job/resumebuild_form.html"

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        return super(ResumeBuildView, self).form_valid(form)


class ResumeDetailView(DetailView):
    context_object_name = 'resume'
    model = Resume
    template_name = 'job/resume_detail.html'

    def get_object(self):
        return get_object_or_404(Resume, pk=self.kwargs['resume_pk'])



class ResumeListView(ListView):
    model = Resume
    template_name='job/resume_list.html'
    context_object_name='resumelist'
    paginate_by= 10

    def get_context_data(self, **kwargs):
        context = super(ResumeListView, self).get_context_data(**kwargs)
        Resumelist = Resume.objects.filter(user=self.request.user)
        context['Resumelist']=Resumelist

        return context
    
class JobPostView(CreateView):

    form_class = JobPostForm
    template_name = "job/job_post_form.html"



    def get_success_url(self, **kwargs):
        organisation = get_object_or_404(Organisation, pk=self.kwargs['organisation_pk'])
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
    
        return reverse('job:joblist', kwargs={'organisation_pk':organisation.pk, 'period_selected_pk':period_selected.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        organisation = Organisation.objects.get(pk=self.kwargs['organisation_pk'])
        form.instance.organisation = organisation
        return super(JobPostView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(JobPostView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected

        return context


class JobPostDetailView(DetailView):
    context_object_name = 'job'
    model = Job
    template_name = 'job/job_post_detail.html'




class JobListView(ListView):
    model = Job
    template_name='job/job_post_list.html'
    paginate_by= 10


    def get_context_data(self, **kwargs):
        context = super(JobListView, self).get_context_data(**kwargs)
        organisation = get_object_or_404(Organisation, pk=self.kwargs['organisation_pk'])
        context['organisation'] = organisation
        period_selected = get_object_or_404(PeriodSelected, pk=self.kwargs['period_selected_pk'])
        context['period_selected'] = period_selected
        joblist = Job.objects.filter(organisation=self.kwargs['organisation_pk'])

        
        context['joblist']=joblist

        return context
    
    