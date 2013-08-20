from django.db import models
from django.utils.translation import ugettext as _
from audit_trail.audit import AuditTrail
from bhp_common.choices import YES_NO
from bcpp_subject.models.base_scheduled_visit_model import BaseScheduledVisitModel


class FollowupContactPermission (BaseScheduledVisitModel):

    """G.Permissions to be contacted for follow-up"""
    contact_permission=models.CharField(
        verbose_name=_("My fellow counselors and I are available to help you"
                       " begin HIV care at the local health clinic.  Do you give"
                       " permission for counselors to contact you by telephone and"
                       " make home visits to make sure you get the care you need"),
        max_length=3,
        choices=YES_NO,
        help_text='',
    )
    
    contact_family=models.CharField(
        verbose_name=_("If we are unable to reach you, would you be willing to have me or"
                       " one of my fellow counselors contact a family member or friend who "
                       "would be able to reach you"),
        max_length=3,
        choices=YES_NO,
        help_text=''
    )
    
    male_contact=models.CharField(
        verbose_name=_("My fellow counselors and I are available to help you decide if circumcision"
                       " is right for you   and to access male circumcision services.  If we try to"
                       " call you and miss you, the caller will not leave any detailed message but"
                       " only his name and number. If someone asks, we will just say we are doing"
                       " mobilization for men’s health.  Do you give permission for counselors"
                       " to contact you by telephone and home visits?"),
        max_length=3,
        choices=YES_NO,
        help_text='',
    )
    
    male_family=models.CharField(
        verbose_name=_("If we are unable to reach you, would you be willing to have me or one"
                       " of my fellow counselors contact a family member or friend who would be"
                       " able to reach you?  The caller will not leave any detailed message but"
                       " only his name and number."),
        max_length=3,
        choices=YES_NO,
        help_text='',                                
    )
    
    pregnant_permission=models.CharField(
        verbose_name=_("It is recommended that pregnant women receive antenatal care for their health"
                       " and their baby’s health.  This care includes an HIV test during the third"
                       " trimester of pregnancy.  Counselors are available to help you receive HIV"
                       " testing during pregnancy.  Do you give permission for counselors to contact"
                       " you by telephone and home visits?"),
        max_length=3,
        choices=YES_NO,
        help_text='',                                
    )
    
    pregnant_family=models.CharField(
        verbose_name=_("If we are unable to reach you, would you be willing to have me or one of my"
                       " fellow counselors contact a family member or friend who would be able to reach you?"),
        max_length=3,
        choices=YES_NO,
        help_text='',                                
    )
     
    history = AuditTrail()

    class Meta:
        app_label = 'bcpp_htc'
        verbose_name = "Permissions to be contacted for follow-up"
        verbose_name_plural = "Permissions to be contacted for follow-ups"
