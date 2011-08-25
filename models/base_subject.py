from django.db import models
from bhp_common.models import MyBasicUuidModel
from bhp_registration.choices import REGISTRATION_STATUS, SUBJECT_TYPE

class BaseSubject (MyBasicUuidModel):
       
    subject_consent_id = models.CharField(
        max_length=100, 
        null = True,
        blank = True,
        )
       
    subject_identifier = models.CharField(
        verbose_name = "Subject Identifier",
        max_length=25, 
        unique=True, 
        )
    
    first_name = models.CharField(
        max_length=50,
        )
    
    initials = models.CharField(
        max_length=3,
        )                    

    gender = models.CharField(
        verbose_name = "Gender",
        max_length=1, 
        null = True,
        blank = True,
        )
        
    subject_type = models.CharField(
        max_length = 25,
        #choices=SUBJECT_TYPE,
        )         
    
    screening_datetime=models.DateTimeField(
        null=True,
        blank=True
        )
    
    registration_datetime=models.DateTimeField(        
        null=True,
        blank=True
        )
    
    """ for simplicity, if going straight from screen to rando, 
        update bothe reg date and rando date """
    randomization_datetime=models.DateTimeField(
        null=True,
        blank=True
        )


    registration_status = models.CharField(
        verbose_name = "Registration status",
        max_length = 25,
        #choices=REGISTRATION_STATUS,
        null = True,
        blank = True,
        )
    
    def __unicode__ (self):
        return "%s %s" % (self.subject_identifier, self.subject_type)
    
    class Meta:
        abstract=True
