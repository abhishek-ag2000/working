"""
Resources
"""
from import_export import resources
from .models import Company


class CompanyResource(resources.ModelResource):
    """
    Company Resource
    """
    class Meta:
        """
        Meta
        """
        model = Company
