from django.contrib import admin
from legal_database.models import Categories, Cases, Central_bare_act, State_bare_act, Chapter, Section, Sub_section
# Register your models here.


class Cases_admin(admin.ModelAdmin):
	model = Cases
	list_display = ['title','date']
	search_fields = ['title','bare_body']

	def get_form(self, request, obj=None, **kwargs):
		form = super(Cases_admin, self).get_form(request, obj, **kwargs)
		form.base_fields['categories'].label_from_instance = lambda obj: "{} {}".format(obj.title, obj.id)
		return form


class Central_bare_act_admin(admin.ModelAdmin):
	model = Central_bare_act
	list_display = ['title','date']
	search_fields = ['title','bare_body']

	def get_form(self, request, obj=None, **kwargs):
		form = super(Central_bare_act_admin, self).get_form(request, obj, **kwargs)
		form.base_fields['cases'].label_from_instance = lambda obj: "{} : {}".format(obj.title, obj.categories)
		return form

class State_bare_act_admin(admin.ModelAdmin):
	model = State_bare_act
	list_display = ['title','date']
	search_fields = ['title','bare_body']

	def get_form(self, request, obj=None, **kwargs):
		form = super(State_bare_act_admin, self).get_form(request, obj, **kwargs)
		form.base_fields['cases'].label_from_instance = lambda obj: "{} : {}".format(obj.title, obj.categories)
		return form

class Section_admin(admin.ModelAdmin):
	model = Section
	search_fields = ['title']

	def get_form(self, request, obj=None, **kwargs):
		form = super(Section_admin, self).get_form(request, obj, **kwargs)
		form.base_fields['cases'].label_from_instance = lambda obj: "{} : {}".format(obj.title, obj.categories)
		return form

class Sub_section_admin(admin.ModelAdmin):
	model = Sub_section
	search_fields = ['title']

	def get_form(self, request, obj=None, **kwargs):
		form = super(Sub_section_admin, self).get_form(request, obj, **kwargs)
		form.base_fields['section'].label_from_instance = lambda obj: "{} : {}".format(obj.number, obj.title)
		return form

admin.site.register(Categories)
admin.site.register(Cases,Cases_admin)
admin.site.register(Central_bare_act,Central_bare_act_admin)
admin.site.register(State_bare_act,State_bare_act_admin)
admin.site.register(Chapter)
admin.site.register(Section,Section_admin)
admin.site.register(Sub_section,Sub_section_admin)

