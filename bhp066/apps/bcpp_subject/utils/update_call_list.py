from django.db.models import get_model

from edc.map.exceptions import MapperError
from edc_constants.constants import NEW, YES

from bhp066.apps.bcpp_survey.models import Survey
from bhp066.apps.bcpp_household.models import HouseholdStructure
from bhp066.apps.bcpp_household_member.models import HouseholdMember
from bhp066.apps.bcpp_household_member.exceptions import HouseholdStructureNotEnrolled


def update_call_list(community, survey_slug, label, verbose=False):
    """Adds information from SubjectConsent instances from the specified survey to the
    CallList model for the current survey.

    If there is no SubjectLocator or subject_locator.may_follow='No', the subject is not added
    to the call list.

    If needed, the household member for the next survey will be created.
    See (HouseholdStructure manager method add_household_members_from_survey).
    """
    SubjectReferral = get_model('bcpp_subject', 'SubjectReferral')
    CallList = get_model('bcpp_subject', 'CallList')
    HicEnrollment = get_model('bcpp_subject', 'HicEnrollment')
    SubjectConsent = get_model('bcpp_subject', 'SubjectConsent')
    SubjectLocator = get_model('bcpp_subject', 'SubjectLocator')
    # Pull all consented members from the supplied survey year (Usually the past survey).
    members = HouseholdMember.objects.filter(household_structure__survey__survey_slug=survey_slug,
        is_consented=True,
        household_structure__household__plot__community=community)
#     consent_options = dict(household_member__household_structure__survey__survey_slug=survey_slug,
#                            community=community)
    options = {}
    n = 0
    # total = SubjectConsent.objects.all().count()
    #total = SubjectConsent.objects.filter(**consent_options).count()
    total = members.count()
    print 'Pulled {} consented members for village {}.'.format(total, community.upper())
    #for subject_consent in SubjectConsent.objects.filter(**consent_options).order_by('subject_identifier'):
    for member in members:
        print 'Now attending to {}, of identifier {}.'.format(member, member.registered_subject.subject_identifier)
        n += 1
        try:
            SubjectLocator.objects.get(
                subject_visit__household_member__internal_identifier=member.internal_identifier,
                may_follow_up=YES)
            try:
                hic_enrollment = HicEnrollment.objects.get(
                    subject_visit__household_member__internal_identifier=member.internal_identifier,
                    hic_permission=YES)
                options.update(
                    hic=True,
                    hic_datetime=hic_enrollment.report_datetime
                )
            except HicEnrollment.DoesNotExist:
                options.update(
                    hic=False,
                    hic_datetime=None,
                )
            try:
                subject_referral = SubjectReferral.objects.get(
                    subject_visit__household_member=member)
                options.update(
                    referral_code=subject_referral.referral_code,
                    referral_appt_date=subject_referral.referral_appt_date,
                )
            except SubjectReferral.DoesNotExist:
                pass
            household = member.household_structure.household
            source_survey = member.household_structure.survey
            target_survey = Survey.objects.current_survey()
            HouseholdStructure.objects.add_household_members_from_survey(
                household, source_survey, target_survey)
            # The current survey
            household_structure = HouseholdStructure.objects.get(
                household=household,
                survey=target_survey)
            target_household_member = HouseholdMember.objects.get(
                household_structure=household_structure,
                internal_identifier=member.internal_identifier)
            # Get the earliest consent.
            subject_consent = SubjectConsent.objects.filter(
                subject_identifier=member.registered_subject.subject_identifier).order_by('version')[0]
            options.update(
                household_member=target_household_member,
                community=household.plot.community,
                first_name=target_household_member.first_name,
                initials=target_household_member.initials,
                age_in_years=target_household_member.age_in_years,
                gender=target_household_member.gender,
                subject_identifier=subject_consent.subject_identifier,
                app_label=SubjectConsent._meta.app_label,
                object_name=SubjectConsent._meta.object_name,
                object_pk=subject_consent.pk,
                bhs=True,
                consent_datetime=subject_consent.consent_datetime,
                call_status=NEW,
                label=label,
                hostname_created=subject_consent.hostname_created,
                user_created=subject_consent.user_created,
            )
            try:
                call_list = CallList.objects.get(household_member=target_household_member, label=label)
                if verbose:
                    print '{}/{} {} already added to call list'.format(n, total, subject_consent.subject_identifier)

            except CallList.DoesNotExist:
                call_list = CallList.objects.create(**options)
                if verbose:
                    print '{}/{} Added {} to call list'.format(n, total, subject_consent.subject_identifier)
            call_list.hostname_created = subject_consent.hostname_created
            call_list.user_created = subject_consent.user_created
            call_list.save()
        except MapperError as e:
            print e
        except SubjectLocator.DoesNotExist:
            print('Not adding {} to call list. No contact information or may not '
                  'follow (SubjectLocator)'.format(subject_consent))
        except HouseholdStructureNotEnrolled as e:
            print str(e)
