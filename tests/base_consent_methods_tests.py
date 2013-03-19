import re
from datetime import datetime
from django.test import TestCase
from bhp_variables.models import StudySpecific
from bhp_registration.models import RegisteredSubject
from bhp_base_model.models import TestForeignKey, TestManyToMany
from bhp_consent.models import TestSubjectConsent, TestSubjectUuidModel, ConsentCatalogue
from bhp_consent.exceptions import ConsentError
from bhp_content_type_map.classes import ContentTypeMapHelper
from bhp_content_type_map.models import ContentTypeMap
from base_methods import BaseMethods
from bhp_registration.tests.factories import RegisteredSubjectFactory
from factories import TestSubjectConsentFactory, ConsentCatalogueFactory


class BaseConsentMethodsTests(TestCase, BaseMethods):

    def setUp(self):
        self.create_study_variables()

    def test_subject_consent_save(self):
        registered_subject = RegisteredSubjectFactory()
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        self.assertTrue(re_pk.match(str(registered_subject.subject_identifier)))
        # create a consent without a user provided identifier
        subject_consent = TestSubjectConsentFactory()
        # assert a new identifier was created
        self.assertIsNotNone(subject_consent.subject_identifier)
        # assert RegisteredSubject was created with this identifier
        self.assertTrue(RegisteredSubject.objects.get(subject_identifier=subject_consent.subject_identifier).subject_identifier, subject_consent.subject_identifier)
        # create new consent but provide a user identifier
        user_provided_subject_identifier = 'TEST_IDENTIFIER'
        subject_consent = TestSubjectConsentFactory(user_provided_subject_identifier=user_provided_subject_identifier)
        print subject_consent.subject_identifier
        # assert user provided identifier was used on the consent model
        self.assertEqual(subject_consent.subject_identifier, user_provided_subject_identifier)
        # assert user provided identifier was used on the RegisteresSubject model
        print [rs.subject_identifier for rs in RegisteredSubject.objects.all()]
        self.assertEqual(RegisteredSubject.objects.filter(subject_identifier=subject_consent.subject_identifier).count(), 1)
        # try to change the user provided identifier
        subject_consent.user_provided_subject_identifier = 'TEST_IDENTIFIER'
        # assert this raises an exception
        self.assertRaises(ConsentError, subject_consent.save)
        # assert subject identifier was not modified
        self.assertEqual(subject_consent.subject_identifier, user_provided_subject_identifier)
        # create an blank RegisteredSubject
        registered_subject = RegisteredSubject.objects.create()
        # create a consent
        subject_consent = TestSubjectConsentFactory()
        # assert identifier was created and registered subject was updated
        self.assertEqual(RegisteredSubject.objects.get(subject_identifier=subject_consent.subject_identifier).subject_identifier, subject_consent.subject_identifier)
        # create a registered subject and specify the subject identifier
        registered_subject = RegisteredSubject.objects.create(subject_identifier="REGISTERED_SUBJECT_ID")
        # create a consent related to the registerred_subject
        subject_consent = TestSubjectConsentFactory()
        # assert the consent used the subject_identifier on registered_subject
        self.assertEqual(subject_consent.subject_identifier, "REGISTERED_SUBJECT_ID")
        # assert the identifier on registered_subject was not changed
        self.assertEqual(RegisteredSubject.objects.get(subject_identifier=subject_consent.subject_identifier).subject_identifier, "REGISTERED_SUBJECT_ID")

    def test_consent_catalogue(self):
        content_type_map_helper = ContentTypeMapHelper()
        content_type_map_helper.populate()
        content_type_map_helper.sync()
        # prepare the consent catalogue
        content_type_map = ContentTypeMap.objects.get(model__iexact=TestSubjectConsent._meta.object_name)
        ConsentCatalogueFactory(content_type_map=content_type_map, add_for_app='bhp_consent')

    def test_subject_uuid_model(self):
        self.test_consent_catalogue()
        test_m2m2 = TestManyToMany.objects.create(name='test_m2m2', short_name='test_m2m2')
        TestManyToMany.objects.create(name='test_m2m3', short_name='test_m2m3')
        TestForeignKey.objects.create(name='test_fk', short_name='test_fk')
        registered_subject = RegisteredSubject.objects.create(subject_identifier="TEST_SUBJECT_UUID")
        TestSubjectConsent.objects.create(
            registered_subject=registered_subject,
            first_name='TEST_SUBJECT_UUID',
            last_name='TEST_SUBJECT_UUIDER',
            user_provided_subject_identifier=None,
            initials='TT',
            identity='111111115',
            confirm_identity='111111115',
            identity_type='omang',
            dob=datetime(1990, 01, 01),
            is_dob_estimated='No',
            gender='M',
            subject_type='subject',
            consent_datetime=datetime.today(),
            study_site=self.study_site,
            may_store_samples='Yes',
            )
        test_subject_uuid_model = TestSubjectUuidModel(
            name='TEST',
            registered_subject=registered_subject,
            test_foreign_key=TestForeignKey.objects.all()[0],
            )
        test_subject_uuid_model.save()
        test_subject_uuid_model.test_many_to_many.add(test_m2m2)
        test_subject_uuid_model = TestSubjectUuidModel.objects.get(pk=test_subject_uuid_model.pk)
        self.assertEqual([m2m.name for m2m in test_subject_uuid_model.test_many_to_many.all()], [test_m2m2.name])
