from django.contrib import admin
from bhp_admin_models.models import MyModelAdmin, MyStackedInline
from bhp_consent_models.models import SubjectIdentifierAuditTrail

class SubjectIdentifierAuditTrailAdmin(MyModelAdmin):
    list_display = (
        'subject_identifier',
        'first_name',
        'initials',
        'date_allocated',
        )
    list_per_page = 15
        
admin.site.register(SubjectIdentifierAuditTrail, SubjectIdentifierAuditTrailAdmin)

