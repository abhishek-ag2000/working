from django.contrib import admin

# Register your models here.
from .models_accounts import Account
# from .models import Tags
# from .models_cases import Case
from .models_contacts import Contact
# from .models_leads import Lead
# from .models_opportunity import Opportunity
# from .models_events import Event
# from .models_tasks import Task
# from .models_teams import Teams

# class TagsAdmin(admin.ModelAdmin):
#     """
#     Model Admin class for TagsAdmin model
#     """
#     model = Tags
#     list_display = ['name', 'slug']
#     search_fields = ['name']

class AccountAdmin(admin.ModelAdmin):
    """
    Model Admin class for AccountAdmin model
    """
    model = Account
    list_display = ['company', 'name','email','phone']
    search_fields = ['company','name']

# class EmailAdmin(admin.ModelAdmin):
#     """
#     Model Admin class for EmailAdmin model
#     """
#     model = Email
#     list_display = ['from_account','from_email', 'message_subject','message_body']
#     search_fields = ['from_account','from_email']

# class EmailLogAdmin(admin.ModelAdmin):
#     """
#     Model Admin class for EmailLogAdmin model
#     """
#     model = Email
#     list_display = ['email','contact', 'is_sent']
#     search_fields = ['email','contact']


# class CaseAdmin(admin.ModelAdmin):
#     """
#     Model Admin class for CaseAdmin model
#     """
#     model = Email
#     list_display = ['company', 'name',  'account', 'status']
#     search_fields = ['company', 'name', ]


class ContactAdmin(admin.ModelAdmin):
    """
    Model Admin class for ContactAdmin model
    """
    model = Contact
    list_display = ['id','company', 'created_by', 'first_name',  'email', 'address']
    search_fields = ['company', 'created_by', 'first_name']


# class LeadAdmin(admin.ModelAdmin):
#     """
#     Model Admin class for LeadAdmin model
#     """
#     model = Lead
#     list_display = ['company', 'created_by', 'title',  'first_name', 'phone']
#     search_fields = ['company', 'created_by', 'title']


# class OpportunityAdmin(admin.ModelAdmin):
#     """
#     Model Admin class for OpportunityAdmin model
#     """
#     model = Opportunity
#     list_display = ['company', 'created_by', 'name', 'account', 'lead_source']
#     search_fields = ['company', 'created_by', 'name']

# class EventAdmin(admin.ModelAdmin):
#     """
#     Model Admin class for EventAdmin model
#     """
#     model = Event
#     list_display = ['company', 'name', 'event_type', 'description', 'status']
#     search_fields = ['company', 'name', 'event_type']


# class TaskAdmin(admin.ModelAdmin):
#     """
#     Model Admin class for TaskAdmin model
#     """
#     model = Task
#     list_display = ['company', 'title', 'created_by', 'status', 'account']
#     search_fields = ['company', 'title', 'created_by']


# class TeamsAdmin(admin.ModelAdmin):
#     """
#     Model Admin class for TeamsAdmin model
#     """
#     model = Teams
#     list_display = ['company', 'name', 'description', 'created_by']
#     search_fields = ['company', 'name', 'description']



# admin.site.register(Tags, TagsAdmin)
admin.site.register(Account, AccountAdmin)
# admin.site.register(Email, EmailAdmin)
# admin.site.register(EmailLog, EmailLogAdmin)
# admin.site.register(Case, CaseAdmin)
admin.site.register(Contact, ContactAdmin)
# admin.site.register(Lead, LeadAdmin)
# admin.site.register(Opportunity, OpportunityAdmin)
# admin.site.register(Event, EventAdmin)
# admin.site.register(Task, TaskAdmin)
# admin.site.register(Teams, TeamsAdmin)
