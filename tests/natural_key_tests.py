import factory
import pprint
from django.test import TestCase
from django.core import serializers
from bhp_crypto.classes import FieldCryptor

from django.db.models import get_app, get_models, get_model
from django.contrib.contenttypes.models import ContentType
from bhp_lab_tracker.classes import site_lab_tracker
from bhp_sync.classes import SerializeToTransaction
from bcpp_subject.tests.factories import SubjectConsentFactory
from bcpp_subject.tests.factories import SubjectVisitFactory, GrantFactory, LabourMarketWagesFactory, SubjectLocatorFactory, \
                                         SubjectAbsenteeEntryFactory, SubjectDeathFactory, SubjectUndecidedEntryFactory, \
                                         SubjectRefusalFactory, SubjectReferralFactory, SubjectMovedFactory
from bhp_variables.tests.factories import StudySpecificFactory, StudySiteFactory
from bhp_registration.models import RegisteredSubject
from bhp_consent.tests.factories import ConsentCatalogueFactory
from bhp_appointment.tests.factories import AppointmentFactory
from bhp_visit.tests.factories import VisitDefinitionFactory
from bhp_content_type_map.tests.factories import ContentTypeMapFactory
from bhp_appointment.models import Appointment
from bcpp_household_member.tests.factories import HouseholdMemberFactory
from bhp_appointment.tests.factories import ConfigurationFactory
from bhp_content_type_map.classes import ContentTypeMapHelper
from bhp_content_type_map.models import ContentTypeMap
from datetime import datetime, timedelta
from bcpp_survey.models import Survey
from bhp_visit.models import VisitDefinition


class NaturalKeyTests(TestCase):

    def test_p1(self):
        """Confirms all models have a natural_key method (except Audit models)"""
        app = get_app('bcpp_subject')
        for model in get_models(app):
            if 'Audit' not in model._meta.object_name:
                print 'checking for natural key on {0}.'.format(model._meta.object_name)
                self.assertTrue('natural_key' in dir(model), 'natural key not found in {0}'.format(model._meta.object_name))

    def test_p2(self):
        """Confirms all models have a get_by_natural_key manager method."""
        app = get_app('bcpp_subject')
        for model in get_models(app):
            if 'Audit' not in model._meta.object_name:
                print 'checking for get_by_natural_key manager method key on {0}.'.format(model._meta.object_name)
                self.assertTrue('get_by_natural_key' in dir(model.objects), 'get_by_natural_key key not found in {0}'.format(model._meta.object_name))

    def test_p3(self):
        site_lab_tracker.autodiscover()
        StudySpecificFactory()
        study_site = StudySiteFactory()
        ConfigurationFactory()
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        print 'setup the consent catalogue for this BCPP'
        content_type_map = ContentTypeMap.objects.get(content_type__model__iexact='SubjectConsent')
        print ContentTypeMap.objects.all().count()
        consent_catalogue = ConsentCatalogueFactory(name='bcpp year 0', content_type_map=content_type_map)
        consent_catalogue.add_for_app = 'bcpp_subject'
        consent_catalogue.save()
        
        print 'consent the subject'
        #SubjectConsentFactory = get_model('bcpp_subject','SubjectConsentFactory')
        Survey.objects.create(survey_name = 'YEAR 0',
                          datetime_start = datetime.today() - timedelta(days=30),
                          datetime_end = datetime.today() + timedelta(days=180)
                          )
#         print 'Clear previous Registered Subjects: Count='+str(RegisteredSubject.objects.all().count())
#         RegisteredSubject.objects.all().delete()
        household_member = HouseholdMemberFactory()
        subject_consent = SubjectConsentFactory(study_site=study_site,household_member=household_member)
        print subject_consent.subject_identifier
        print 'get registered subject'
        registered_subject = RegisteredSubject.objects.get(subject_identifier=subject_consent.subject_identifier)
        instances = []
        instances.append(subject_consent)
        instances.append(registered_subject)

        print 'test natural key / get_by_natural_key on subject_visit'
        
#         appointment, created = Appointment.objects.get_or_create(registered_subject=registered_subject,
#                                                                  appt_datetime = datetime.today(),
#                                                                  visit_definition__code='1000')
        content_type = ContentType.objects.get(app_label='bcpp_subject',model='subjectvisit')
        content_type_map = ContentTypeMap.objects.get(content_type=content_type)
        visit_definition = VisitDefinitionFactory(visit_tracking_content_type_map=content_type_map)
        appointment = AppointmentFactory(registered_subject=registered_subject, visit_definition=visit_definition)
        subject_visit = SubjectVisitFactory(appointment=appointment)
        #BloodDraw : for BaseScheduledVisitModels, REPLACED BY CD4_HISTORY
        #Grant: Independent Natural Key
        labour_market_wages = LabourMarketWagesFactory(subject_visit=subject_visit)
        grant = GrantFactory(labour_market_wages=labour_market_wages, subject_visit=subject_visit)#Investigate natural keys further
        #SubjectAbsentee : for BaseRegisteredHouseholdMemberModel
        from bcpp_subject.tests.factories import SubjectAbsenteeFactory
        subject_absentee = SubjectAbsenteeFactory(household_member=household_member, registered_subject=registered_subject)
        from bcpp_subject.tests.factories import SubjectUndecidedFactory
        subject_undecided = SubjectUndecidedFactory(household_member=household_member, registered_subject=registered_subject)
        subject_refusal = SubjectRefusalFactory(household_member=household_member)
        subject_referral = SubjectReferralFactory(household_member=household_member, registered_subject=registered_subject)
        subject_moved = SubjectMovedFactory(household_member=household_member, registered_subject=registered_subject)
        #SubjectAbsenteeEntry : Independent Natural Key
        subject_absentee_entry = SubjectAbsenteeEntryFactory(subject_absentee=subject_absentee)
        subject_undecided_entry = SubjectUndecidedEntryFactory(subject_undecided=subject_undecided)     
        #SubjectDeath : Independent Natural Keys
        subject_death = SubjectDeathFactory(registered_subject=registered_subject)
        #SubjectLocator : Independent Natural Key
        subject_locator = SubjectLocatorFactory(subject_visit=subject_visit, registered_subject=registered_subject)
        #SubjectOffStudy :
        #subject_off_study = 
        instances.append(grant)
        instances.append(subject_absentee)
        instances.append(subject_undecided)
        instances.append(subject_refusal)
        instances.append(subject_referral)
        instances.append(subject_moved)
        instances.append(subject_death)
        instances.append(subject_locator)
        instances.append(subject_absentee_entry)
        instances.append(subject_undecided_entry)
        
        print 'INSTANCE: '+str(instances)
        for obj in instances:
            print 'test natural key on {0}'.format(obj._meta.object_name)
            natural_key = obj.natural_key()
            get_obj = obj.__class__.objects.get_by_natural_key(*natural_key)
            self.assertEqual(obj.pk, get_obj.pk)
        #pp = pprint.PrettyPrinter(indent=4)
        for obj in instances:
            print 'test serializing/deserializing {0}'.format(obj._meta.object_name)
            outgoing_transaction = SerializeToTransaction().serialize(obj.__class__, obj)
            #pp.pprint(FieldCryptor('aes', 'local').decrypt(outgoing_transaction.tx))
            for transaction in serializers.deserialize("json", FieldCryptor('aes', 'local').decrypt(outgoing_transaction.tx)):
                self.assertEqual(transaction.object.pk, obj.pk)
