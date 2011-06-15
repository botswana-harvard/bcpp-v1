from django.db import models
from base_subject import BaseSubject


class RegisteredSubjectManager(models.Manager):
    
    """Manager class for RegisteredSubject model."""
    
    def register_subject(consent_model, subject_type='SUBJECT', user=''):
        
        """
        Register a subject by allocating an identifier at the time of consent and storing in model RegisteredSubject.
        
        Generate an identifier and save it back to the consent form 
        and update the identifier audit trail.
        
        The consent_model is the selected and new consent. Count=1
            
        """
        subject_identifier = {}
        
        #get the consent just created
        #consent = SubjectConsent.objects.get(pk=new_pk)

        subject_identifier['site'] = consent_model.study_site.site_code
        
        #add a new record in the audit trail for this consent and identifier-'to be'
        #leave subject_identifier 'null' for now
        audit = SubjectIdentifierAuditTrail(
            subject_consent_id=consent_model.pk, 
            first_name = consent_model.first_name,
            initials = consent_model.initials,
            date_allocated=datetime.now(),
            user_created = user,
            )
            
        audit.save()    


        # get the auto-increment id for the new audit trail record
        # just created above
        subject_identifier['audit_id'] = audit.pk

        # prepare the subject identifier by 
        # getting the seed and prefix and deviceid, modulus
        settings = StudySpecific.objects.all()[0]
        subject_identifier['modulus'] = settings.subject_identifier_modulus
        subject_identifier['seed'] = settings.subject_identifier_seed
        subject_identifier['prefix']= settings.subject_identifier_prefix
        subject_identifier['device_id']= settings.device_id
        
        if subject_identifier['seed'] == 99:
            raise TypeError("Subject_identifier_seed cannot be 99. Did you configure bhp_variables.StudySpecific?")
            
        # using the seed, device and audit trail id determine the integer segment of the id 
        subject_identifier['int'] = (((subject_identifier['seed']* subject_identifier['device_id']) + subject_identifier['audit_id'])) 

        # using the integer segment, calculate the check digit
        check_digit = subject_identifier['int'] % subject_identifier['modulus']

        # pad the check digit if required based on the modulus
        if subject_identifier['modulus'] > 100 and subject_identifier['modulus'] <= 1000:
            if check_digit <10:
                subject_identifier['check_digit'] = "00%s" % (check_digit)
            if check_digit >=10 and check_digit < 100:
                subject_identifier['check_digit'] = "%0s" % (check_digit)    
            if check_digit >=100 and check_digit < 1000:
                subject_identifier['check_digit'] = "%s" % (check_digit)                

        if subject_identifier['modulus'] > 10 and subject_identifier['modulus'] <= 100:
            if check_digit <10:
                subject_identifier['check_digit'] = "0%s" % (check_digit)
            if check_digit >=10 and check_digit < 100:
                subject_identifier['check_digit'] = "%s" % (check_digit)    
        
        if subject_identifier['modulus'] <= 10:
            subject_identifier['check_digit'] = "%s" % (check_digit) 

        #create the formatted identifier
        subject_identifier['identifier'] = "%s-%s%s-%s" % (subject_identifier['prefix'], subject_identifier['site'],subject_identifier['int'],  subject_identifier['check_digit'] )
       
        # update subject_identifier to the audit trail table
        audit.subject_identifier = subject_identifier['identifier']
        audit.save()
        
        RegisterSubject(
            identifier=subject_identifier['identifier'], 
            consent_pk=consent_model.pk, 
            first_name=consent_model.first_name, 
            initials=consent_model.initials, 
            subject_type=subject_type, 
            user=user)
        
        # return the new subject identifier to the form currently being save()'d
        return subject_identifier['identifier']

    def register_live_infants(** kwargs):

        """
        Allocate infant identifiers for as many live_infants_to_register.
        
        Choose an id_suffix based on the value of live_infants. So if 
        live_infants <> live_infants_to_register, use live_infants to
        determine the suffix, and live_infants_to_register for the number
        to register
        
        """

        registration_model = kwargs.get('registration_model')
        registered_mother = kwargs.get('mother_identifier')
        live_infants = kwargs.get('live_infants')
        live_infants_to_register = kwargs.get('live_infants_to_register')
        user = kwargs.get('user')

        if live_infants_to_register > live_infants:
            # Trap this on the form, not here!!
            raise TypeError("Number of infants to register may not exceed number of live infants.")
        
        subject_identifier = {}

        subject_identifier['mother'] = registered_mother.subject_identifier   
        
        # we use the mother's consent as the consent pk to store in 
        # registered subject for this/these infant(s)

        first_name=''
        initials=''
        id_suffix = 0

        if live_infants == 1:
            id_suffix = 10
        elif live_infants == 2:
            id_suffix = 25
        elif live_infants == 3:
            id_suffix = 36
        elif live_infants == 4:
            id_suffix = 47
        else:
            raise TypeError('Ensure number of infants is greater than 0 and less than or equal to 4. You wrote %s' % (live_infants))

        for infant_order in range(0, live_infants_to_register):
            id_suffix += (infant_order) * 10
            subject_identifier['id'] = "%s-%s" % (subject_identifier['mother'], id_suffix)            
            RegisterSubject(
                identifier = subject_identifier['id'], 
                relative_identifier = registered_mother.subject_identifier,
                consent_pk = registered_mother.pk, 
                first_name = first_name, 
                initials = initials, 
                subject_type = 'infant', 
                user = user)

        # update subject_identifier to the audit trail table
        # audit.subject_identifier = subject_identifier['identifier']
        # audit.save()
        
        
        return True


class RegisteredSubject(BaseSubject):

    sid = models.CharField(
        verbose_name = "Randomization SID",
        max_length = 15,
        null = True,
        blank = True,
        )
        
    relative_identifier = models.CharField(        
        verbose_name = "Identifier of immediate relation",
        max_length = 25,
        null = True,
        blank = True,
        help_text = "For example, mother's identifier, if available / appropriate"
        )

    objects = RegisteredSubjectManager()
        
    def __unicode__ (self):
        return "%s %s (%s)" % (self.subject_identifier, self.subject_type, self.first_name)

    class Meta:
        app_label = 'bhp_registration'            

