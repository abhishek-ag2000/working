from django.conf.urls import url
from legal_database import views

app_name = 'legal_database'

urlpatterns = [

	url(r'^$',views.Categories_List_View.as_view(),name='categorieslist'),  
	url(r'^(?P<pk>\d+)/central/$',views.Central_bare_act_detail,name='central_act'),
	url(r'^(?P<pk>\d+)/state/$',views.State_bare_act_detail,name='state_act'),  
	url(r'^(?P<pk>\d+)/section/$',views.Section_detail,name='section_act'), 

]
