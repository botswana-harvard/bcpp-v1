from django.db import models

from edc_base.encrypted_fields import IdentityField

from .base_cdc import BaseCdc


class CdcSmcDigawana(BaseCdc):

    Alt_Contact_Made = models.CharField(max_length=25, null=True)
    Contact1_Made = models.CharField(max_length=25, null=True)
    Contact2_Made = models.CharField(max_length=25, null=True)
    Contact3_Made = models.CharField(max_length=25, null=True)
    SMC_Followup_UID = models.IntegerField(null=True)
    Source_System_Name = models.CharField(max_length=25, null=True)
    identity_value = IdentityField(null=True)
    identity_type = models.CharField(max_length=25, null=True)
    mcVstIDtypeOM = IdentityField(null=True)
    mcVstIDtypePBC = IdentityField(null=True)
    mcVstInfoApptdt = models.DateField(null=True)
    mcVstInfoDOB = models.DateField(null=True)
    mcVstInfoDOBnoAge = models.IntegerField(null=True)
    mcVstInfoReslt = models.IntegerField(null=True)
    mcVstInfoSourceDate = models.DateField(null=True)
    mcVstSID = models.CharField(max_length=25, null=True)
    mcfuAltCdate = models.DateField(null=True)
    mcfuCdate1 = models.DateField(null=True)
    mcfuCdate2 = models.DateField(null=True)
    mcfuCdate3 = models.DateField(null=True)
    mcocmc = models.IntegerField(null=True)
    mcocmcdate = models.DateField(null=True)

    class Meta:
        app_label = 'bcpp_stats'
