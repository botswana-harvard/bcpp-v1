from __future__ import print_function

from datetime import datetime
from dateutil.relativedelta import relativedelta

from django import forms
from django.test import TestCase
from django.core.exceptions import ValidationError

from edc.map.classes import Mapper, site_mappers
from edc.subject.appointment.tests.factories import ConfigurationFactory
from edc.subject.consent.tests.factories import ConsentCatalogueFactory
from edc.core.bhp_variables.tests.factories import StudySpecificFactory, StudySiteFactory

from apps.bcpp_household.models import HouseholdStructure
from apps.bcpp_household.tests.factories import PlotFactory
from apps.bcpp_household_member.tests.factories import HouseholdMemberFactory
from apps.bcpp_survey.tests.factories import SurveyFactory

from ..forms import SubjectConsentForm

from .factories import SubjectConsentFactory


class TestPlotMapper(Mapper):
    map_area = 'test_community2'
    map_code = '099'
    regions = []
    sections = []
    landmarks = []
    gps_center_lat = -25.033194
    gps_center_lon = 25.747132
    radius = 5.5
    location_boundary = ()

site_mappers.register(TestPlotMapper)


class FormsTests(TestCase):

    def setUp(self):
        StudySpecificFactory()
        StudySiteFactory()
        ConfigurationFactory()
        self.survey = SurveyFactory()
        self.plot = PlotFactory(community='test_community2', household_count=1, status='occupied')
        self.household_structure = HouseholdStructure.objects.get(household__plot=self.plot)
        self.household_member = HouseholdMemberFactory(household_structure=self.household_structure)

    def test_subject_consent_form1(self):
        """Cannot consent if household_member.eligible_subject = False."""
        self.household_member.eligible_subject = False
        self.assertRaisesRegexp(ValidationError, 'Subject\ is\ not\ eligible', SubjectConsentFactory, household_member=self.household_member)
        data = {'household_member': self.household_member}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'Subject\ is\ not\ eligible', subject_consent_form.clean)

    def test_subject_consent_form2(self):
        """Minor cannot consent if no guardian name."""
        self.household_member.eligible_subject = True
        data = {'household_member': self.household_member,
                'is_minor': 'Yes'}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'subject\ is\ a\ minor\ but\ have\ not\ provided\ the\ guardian\'s\ name', subject_consent_form.clean)

    def test_subject_consent_form3(self):
        """Non-Minor cannot consent if has guardian name."""
        self.household_member.eligible_subject = True
        data = {'household_member': self.household_member,
                'is_minor': 'No',
                'guardian_name': 'JOHNSON'}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'subject\ is\ NOT\ a\ minor.\ Guardian\'s\ name\ is\ not\ required', subject_consent_form.clean)

    def test_subject_consent_form4(self):
        """Cannot consent if too young (<16y)."""
        self.household_member.eligible_subject = True
        data = {'household_member': self.household_member,
                'is_minor': 'Yes',
                'guardian_name': 'JOHNSON',
                'consent_datetime': datetime.today(),
                'dob': datetime.today()}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'Subject is too young to consent', subject_consent_form.clean)
        self.household_member.eligible_subject = True
        data = {'household_member': self.household_member,
                'is_minor': 'No',
                'consent_datetime': datetime.today(),
                'dob': datetime.today()}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'Subject is too young to consent', subject_consent_form.clean)

    def test_subject_consent_form5(self):
        """Fails if minor by age but minor=No."""
        self.household_member.eligible_subject = True
        data = {'household_member': self.household_member,
                'is_minor': 'No',
                'guardian_name': 'JOHNSON',
                'consent_datetime': datetime.today(),
                'dob': datetime.today() + relativedelta(years=-17)}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'subject\ is\ NOT\ a\ minor.\ Guardian\'s\ name\ is\ not\ required', subject_consent_form.clean)

    def test_subject_consent_form6(self):
        """Fails if not minor by age but minor=Yes."""
        self.household_member.eligible_subject = True
        data = {'household_member': self.household_member,
                'is_minor': 'Yes',
                'consent_datetime': datetime.today(),
                'dob': datetime.today() + relativedelta(years=-17)}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'subject is a minor but have not provided the guardian\'s name', subject_consent_form.clean)

    def test_subject_consent_form7(self):
        """Fails if subject is too old."""
        self.household_member.eligible_subject = True
        data = {'household_member': self.household_member,
                'is_minor': 'Yes',
                'guardian_name': 'JOHNSON',
                'consent_datetime': datetime.today(),
                'dob': datetime.today() + relativedelta(years=-99)}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'Subject is too old', subject_consent_form.clean)

    def test_subject_consent_form8(self):
        """Fails if not minor by age but minor=Yes and guardian name provided."""
        self.household_member.eligible_subject = True
        data = {'household_member': self.household_member,
                'is_minor': 'Yes',
                'guardian_name': 'JOHNSON',
                'consent_datetime': datetime.today(),
                'dob': datetime.today() + relativedelta(years=-17)}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'Identity cannot be None', subject_consent_form.clean)

    def test_subject_consent_form9(self):
        """Identify and confirmation must match."""
        self.household_member.eligible_subject = True
        data = {'household_member': self.household_member,
                'is_minor': 'Yes',
                'guardian_name': 'JOHNSON',
                'consent_datetime': datetime.today(),
                'dob': datetime.today() + relativedelta(years=-17),
                'identity_type': 'omang',
                'identity': '123456789',
                'confirm_identity': '123456780'}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'Identity numbers do not match', subject_consent_form.clean)

    def test_subject_consent_form10(self):
        """Identify and confirmation must match."""
        self.household_member.eligible_subject = True
        data = {'household_member': self.household_member,
                'is_minor': 'Yes',
                'guardian_name': 'JOHNSON',
                'consent_datetime': datetime.today(),
                'dob': datetime.today() + relativedelta(years=-17),
                'identity_type': 'omang',
                'identity': '123456789',
                'confirm_identity': '123456789',
                'first_name': 'ERIK',
                'last_name': 'JOHN',
                'initials': 'JJ'}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'initial does not match first name', subject_consent_form.clean)

    def test_subject_consent_form11(self):
        """report datetime must be between survey start and end datetime."""
        self.household_member.eligible_subject = True
        self.household_member.initials = 'EW'
        data = {'household_member': self.household_member,
                'is_minor': 'Yes',
                'guardian_name': 'JOHNSON',
                'consent_datetime': datetime.today(),
                'dob': datetime.today() + relativedelta(years=-17),
                'identity_type': 'omang',
                'identity': '123456789',
                'confirm_identity': '123456789',
                'report_datetime': datetime(2013, 10, 10),
                'initials': 'DS'}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'Initials for household member record do not match', subject_consent_form.clean)

    def test_subject_consent_form12(self):
        """report datetime must be between survey start and end datetime."""
        self.household_member.eligible_subject = True
        self.household_member.initials = 'DS'
        self.household_member.first_name = 'DAVID'
        data = {'household_member': self.household_member,
                'is_minor': 'Yes',
                'guardian_name': 'JOHNSON',
                'consent_datetime': datetime.today(),
                'dob': datetime.today() + relativedelta(years=-17),
                'identity_type': 'omang',
                'identity': '123456789',
                'confirm_identity': '123456789',
                'report_datetime': datetime(2013, 10, 10),
                'initials': 'DS',
                'first_name': 'DON'}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'First name does not match', subject_consent_form.clean)

    def test_subject_consent_form13(self):
        """report datetime must be between survey start and end datetime."""
        self.household_member.eligible_subject = True
        self.household_member.initials = 'DS'
        self.household_member.first_name = 'DAVID'
        self.household_member.gender = 'F'
        data = {'household_member': self.household_member,
                'is_minor': 'Yes',
                'guardian_name': 'JOHNSON',
                'consent_datetime': datetime.today(),
                'dob': datetime.today() + relativedelta(years=-17),
                'identity_type': 'omang',
                'identity': '123456789',
                'confirm_identity': '123456789',
                'report_datetime': datetime(2013, 10, 10),
                'initials': 'DS',
                'first_name': 'DAVID',
                'gender': 'M'}
        subject_consent_form = SubjectConsentForm()
        subject_consent_form.cleaned_data = data
        self.assertRaisesRegexp(forms.ValidationError, 'Gender does not match', subject_consent_form.clean)

#     app_label = 'bcpp_subject'
# 
#     def test_all_forms(self):
#         site_lab_tracker.autodiscover()
#         study_specific = StudySpecificFactory()
#         StudySiteFactory()
#         ConfigurationFactory()
# 
#         content_type_map_helper = ContentTypeMapHelper()
#         content_type_map_helper.populate()
#         content_type_map_helper.sync()
#         #content_type_map = ContentTypeMap.objects.get(model__iexact=SubjectConsent._meta.object_name)
#         ConsentCatalogueFactory(
#             name=self.app_label,
#             #content_type_map=content_type_map,
#             consent_type='study',
#             version=1,
#             start_datetime=study_specific.study_start_datetime,
#             end_datetime=datetime(datetime.today().year + 5, 1, 1),
#             add_for_app=self.app_label)
# 
#         adminuser = User.objects.create_user('django', 'django@test.com', 'pass')
#         adminuser.save()
#         adminuser.is_staff = True
#         adminuser.is_active = True
#         adminuser.is_superuser = True
#         adminuser.save()
#         self.client.login(username=adminuser.username, password='pass')
# 
#         content_type_map = ContentTypeMap.objects.get(content_type__model='EnrolmentChecklist'.lower())
#         membership_form = MembershipFormFactory(content_type_map=content_type_map)
#         schedule_group = ScheduleGroupFactory(membership_form=membership_form, group_name='enrolment', grouping_key='ELIGIBILITY')
#         visit_tracking_content_type_map = ContentTypeMap.objects.get(content_type__model='subjectvisit')
#         visit_definition = VisitDefinitionFactory(code='1000', title='Enrolment', grouping='subject', visit_tracking_content_type_map=visit_tracking_content_type_map)
#         visit_definition.schedule_group.add(schedule_group)
# 
#         survey = SurveyFactory()
#         household = HouseholdFactory()
#         household_structure = HouseholdStructureFactory(household=household, survey=survey)
#         HouseholdMemberFactory(household_structure=household_structure)
#         HouseholdMemberFactory(household_structure=household_structure)
#         HouseholdMemberFactory(household_structure=household_structure)
#         household_member = HouseholdMemberFactory(household_structure=household_structure)
# 
#         subject_consent = SubjectConsentFactory(household_member=household_member)
#         print(subject_consent.registered_subject)
#         registered_subject = RegisteredSubject.objects.get(subject_identifier=subject_consent.subject_identifier)
#         self.assertEqual(subject_consent.registered_subject.pk, registered_subject.pk)
# 
#         enrolment = EnrolmentChecklistFactory(registered_subject=registered_subject)
# 
#         self.assertEqual(Appointment.objects.all().count(), 1)
#         appointment = Appointment.objects.get(registered_subject=registered_subject)
#         self.assertEqual(appointment.registered_subject.pk, registered_subject.pk)
# 
#         subject_visit = SubjectVisitFactory(appointment=appointment)
#         n = 0
#         # collect inline models
#         inline_models = []
#         for model, model_admin in admin.site._registry.iteritems():
#             if self.app_label == model._meta.app_label:
#                 inline_models = inline_models + [m.model for m in model_admin.inlines]
#         print('Inline models are {0}'.format(', '.join([m._meta.object_name for m in inline_models])))
#         for model, model_admin in admin.site._registry.iteritems():
#             if self.app_label == model._meta.app_label:
#                 if issubclass(model, BaseScheduledVisitModel) and model not in inline_models:
#                     n += 1
#                     model_name = model._meta.object_name
#                     print('{0}_{1}_add'.format(model._meta.app_label, model_name.lower()))
#                     url = reverse('admin:{0}_{1}_add'.format(model._meta.app_label, model_name.lower()))
#                     response = self.client.get(url)
#                     print('  assert response=200')
#                     self.assertEqual(response.status_code, 200)
#                     print('  assert template')
#                     self.assertTemplateUsed(response, 'admin/change_form.html')
#                     factory_mod = __import__('bcpp_subject.tests.factories', fromlist=['{0}Factory'.format(model_name)])
#                     factory = getattr(factory_mod, '{0}Factory'.format(model_name))
#                     print('  instantiate the factory')
#                     model_instance = factory(subject_visit=subject_visit)
#                     print('  subject_visit = {0}'.format(model_instance.subject_visit))
#                     print('  get admin change url for pk={0}'.format(model_instance.id))
#                     url = reverse('admin:{0}_{1}_change'.format(model_instance._meta.app_label, model_instance._meta.object_name.lower()), args=(model_instance.id, ))
#                     print('  url = {0}'.format(url))
#                     print('  subject_visit.get_subject_identifier() = {0}'.format(model_instance.subject_visit.get_subject_identifier()))
#                     if model_admin.inlines:
#                         for inline_admin in model_admin.inlines:
#                             print('  inline model {0}'.format(inline_admin.model))
#                             print('    {0}_{1}_add'.format(inline_admin.model._meta.app_label, inline_admin.model._meta.object_name.lower()))
#                             url = reverse('admin:{0}_{1}_add'.format(inline_admin.model._meta.app_label, inline_admin.model._meta.object_name.lower()))
#                             response = self.client.get(url)
#                             print('    assert response=200')
#                             self.assertEqual(response.status_code, 200)
#                             print('    assert template')
#                             self.assertTemplateUsed(response, 'admin/change_form.html')
#                             factory_mod = __import__('bcpp_subject.tests.factories', fromlist=['{0}Factory'.format(inline_admin.model._meta.object_name)])
#                             factory = getattr(factory_mod, '{0}Factory'.format(inline_admin.model._meta.object_name))
#                             print('    instantiate the factory {0}'.format(factory))
#                             factory(**{convert_from_camel(model_instance._meta.object_name): model_instance, 'subject_visit': model_instance.subject_visit})
#                             factory(**{convert_from_camel(model_instance._meta.object_name): model_instance, 'subject_visit': model_instance.subject_visit})
#                     #print('  post url')
#                     #response = self.client.post(url, model_instance.__dict__)
#                     #self.assertEqual(response.status_code, 200)
#         print('tested {0} forms'.format(n))
