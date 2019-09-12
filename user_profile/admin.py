"""
Admin
"""
from django.contrib import admin
from .models import Profile, ProductActivated, RoleBasedProductActivated
from .models import Post, PostComment, ProfessionalServices, Achievement, ProfessionalVerifyDoc, ProfessionalVerify


admin.site.register(Profile)
admin.site.register(ProductActivated)
admin.site.register(RoleBasedProductActivated)
admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(ProfessionalServices)
admin.site.register(Achievement)
admin.site.register(ProfessionalVerifyDoc)
admin.site.register(ProfessionalVerify)
