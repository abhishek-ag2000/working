from import_export import resources
from .models import company

class CompanyResource(resources.ModelResource):
	class Meta:
		model = company
