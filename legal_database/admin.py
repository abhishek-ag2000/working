"""
Admin
"""
from django.contrib import admin
from legal_database.models import Categories, Cases, CentralBareAct, StateBareAct, Chapter, Section, SubSection


class CasesAdmin(admin.ModelAdmin):
    """
    Model Admin class for Cases Model
    """
    model = Cases
    list_display = ['title', 'date']
    search_fields = ['title', 'bare_body']

    def get_form(self, request, obj=None, **kwargs):
        form = super(CasesAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['categories'].label_from_instance = lambda obj: "{} {}".format(
            obj.title, obj.id)
        return form


class CentralBareActAdmin(admin.ModelAdmin):
    """
    Model Admin class for CentralBareAct Model
    """
    model = CentralBareAct
    list_display = ['title', 'date']
    search_fields = ['title', 'bare_body']

    def get_form(self, request, obj=None, **kwargs):
        form = super(CentralBareActAdmin, self).get_form(
            request, obj, **kwargs)
        form.base_fields['cases'].label_from_instance = lambda obj: "{} : {}".format(
            obj.title, obj.categories)
        return form


class StateBareActAdmin(admin.ModelAdmin):
    """
    Model Admin class for StateBareAct Model
    """
    model = StateBareAct
    list_display = ['title', 'date']
    search_fields = ['title', 'bare_body']

    def get_form(self, request, obj=None, **kwargs):
        form = super(StateBareActAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['cases'].label_from_instance = lambda obj: "{} : {}".format(
            obj.title, obj.categories)
        return form


class SectionAdmin(admin.ModelAdmin):
    """
    Model Admin class for Section Model
    """
    model = Section
    search_fields = ['title']

    def get_form(self, request, obj=None, **kwargs):
        form = super(SectionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['cases'].label_from_instance = lambda obj: "{} : {}".format(
            obj.title, obj.categories)
        return form


class SubSectionAdmin(admin.ModelAdmin):
    """
    Model Admin class for SubSection Model
    """
    model = SubSection
    search_fields = ['title']

    def get_form(self, request, obj=None, **kwargs):
        form = super(SubSectionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['section'].label_from_instance = lambda obj: "{} : {}".format(
            obj.number, obj.title)
        return form


admin.site.register(Categories)
admin.site.register(Cases, CasesAdmin)
admin.site.register(CentralBareAct, CentralBareActAdmin)
admin.site.register(StateBareAct, StateBareActAdmin)
admin.site.register(Chapter)
admin.site.register(Section, SectionAdmin)
admin.site.register(SubSection, SubSectionAdmin)
