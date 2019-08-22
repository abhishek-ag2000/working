from django.conf.urls import url
from .views import ResumeBuildView, JobPostView, ResumeDetailView, JobPostDetailView,JobListView,ResumeListView
from . import views

app_name = 'job'

urlpatterns = [

    url(r'^$', views.ResumeBuildView.as_view(), name='create-resume'),
    url(r'^resume/list/$',views.ResumeListView.as_view(),name='resumelist'),
    url(r'^(?P<resume_pk>\d+)/resume/$',views.ResumeDetailView.as_view(),name='resume'),
    url(r'^(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/create/$', views.JobPostView.as_view(), name='post-job'),
    url(r'^(?P<organisation_pk>\d+)/date/(?P<period_selected_pk>\d+)/joblist/$',views.JobListView.as_view(),name='joblist'),
    url(r'^post/(?P<pk>\d+)/$',views.JobPostDetailView.as_view(),name='job'),

]
