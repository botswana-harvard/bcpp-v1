from django.contrib import admin
from bhp_common.models import MyModelAdmin, MyStackedInline
from models import RegisteredSubject, RandomizedSubject, SubjectIdentifierAuditTrail

class RegisteredSubjectAdmin (MyModelAdmin):



    list_display = (
        'subject_identifier',
        'first_name',
        'initials',
        'gender',
        'subject_type',
        'sid',     
        'registration_status',           
        'study_site',
        'user_created',
        'created',

    )   
    
    readonly_fields = (
        'subject_identifier',
        )

    search_fields = ('subject_identifier', 'first_name', 'initials', 'sid', 'identity')    

    
    list_filter = ('subject_type', 'registration_status', 'registration_datetime','gender','study_site',)
    
admin.site.register(RegisteredSubject, RegisteredSubjectAdmin)

admin.site.register(RandomizedSubject)


class SubjectIdentifierAuditTrailAdmin(MyModelAdmin):
    
    list_display = (
        'subject_identifier',
        'first_name',
        'initials',
        'date_allocated',
        )
    list_per_page = 15
        
admin.site.register(SubjectIdentifierAuditTrail, SubjectIdentifierAuditTrailAdmin)

