from datetime import date
from dateutil.relativedelta import relativedelta
from django import forms
from edc.core.bhp_variables.choices import GENDER_OF_CONSENT
from edc.core.bhp_common.utils import formatted_age
from edc.base.form.forms import BaseModelForm


class BaseSubjectConsentForm(BaseModelForm):
    """Form for models that are a subclass of BaseConsent."""
    def clean(self):

        cleaned_data = self.cleaned_data

        if not cleaned_data.get("gender", None):
            raise forms.ValidationError('Please specify the gender')

        # check omang if identity_type is omang
        # encrypted fields may cause problems if existing values
        # cannot be decrypted, so call a custom field method validate_with_cleaned_data()
        # to validate.
        for field in self._meta.model._meta.fields:
            try:
                field.validate_with_cleaned_data(field.attname, cleaned_data)
            except AttributeError:
                pass

        """
        check 1st and last letters of initials match subjects name
        """
        #        my_first_name = cleaned_data.get("first_name")
        #        my_last_name = cleaned_data.get("last_name")
        #        my_initials = cleaned_data.get("initials"
        #        check_initials_field(my_first_name, my_last_name, my_initials)

        """
        if minor, force specify guardian's name
        """
#         try:
#             obj = StudySpecific.objects.all()[0]
#         except IndexError:
#             raise TypeError("Please add your bhp_variables site specifics")

        # Get date the subject was consented so that when we validate consent age
        # we get the age of the subject at the time of the consent
        if cleaned_data.get('consent_datetime', None):
            consent_datetime = cleaned_data.get('consent_datetime').date()
        else:
            consent_datetime = date.today()

        if cleaned_data.get('dob', None):
            rdelta = relativedelta(consent_datetime, cleaned_data.get('dob'))
            if rdelta.years < self._meta.model.Constants.MIN_AGE_OF_CONSENT:
                raise forms.ValidationError(u'Subject\'s age is %s. Subject is not eligible for consent.' % (formatted_age(cleaned_data.get('dob'), date.today())))
            # check if guardian name is required
            # guardian name is required if subject is a minor but the field may not be on the form
            # if the study does not have minors.
            if rdelta.years < self._meta.model.Constants.AGE_IS_ADULT:
                if "guardian_name" not in cleaned_data.keys():
                    raise forms.ValidationError('Subject is a minor. "guardian_name" is required but missing from the form. Please add this field to the form.')
                elif not cleaned_data.get("guardian_name", None):
                    raise forms.ValidationError(u'Subject\'s age is %s. Subject is a minor. Guardian\'s name is required here and with signature on the paper document.' % (formatted_age(cleaned_data.get('dob'), date.today())))
                # elif not re.match(r'\w+\,\ \w+', cleaned_data.get("guardian_name", '')):
                #    raise forms.ValidationError('Invalid format for guardian name. Expected format \'FIRSTNAME, LASTNAME\'.')
                else:
                    pass
            if rdelta.years >= self._meta.model.Constants.AGE_IS_ADULT and "guardian_name" in cleaned_data.keys():
                if not cleaned_data.get("guardian_name", None) == '':
                    raise forms.ValidationError(u'Subject\'s age is %s. Subject is an adult. Guardian\'s name is NOT required.' % (formatted_age(cleaned_data.get('dob'), date.today())))
        # if consent model has a ConsentAge method that returns an ordered range of ages as list
        if hasattr(self._meta.model, 'ConsentAge'):
            instance = self._meta.model()
            consent_age_range = instance.ConsentAge()
            rdelta = relativedelta(consent_datetime, cleaned_data.get('dob'))
            if rdelta.years not in consent_age_range:
                raise forms.ValidationError("Invalid Date of Birth. Age of consent must be between %sy and %sy inclusive. Got %sy" % (consent_age_range[0], consent_age_range[-1], rdelta.years,))

        # check for gender of consent
        if cleaned_data.get('gender'):
            if cleaned_data.get('gender') not in self._meta.model.Constants.GENDER_OF_CONSENT:
                raise forms.ValidationError(
                    'Expected gender to be one of {}. Got {}.'.format(
                        self._meta.model.Constants.GENDER_OF_CONSENT, cleaned_data.get('gender')))
        # confirm attr identity and confirm_identity match
        if cleaned_data.get('identity') and cleaned_data.get('confirm_identity'):
            if cleaned_data.get('identity') != cleaned_data.get('confirm_identity'):
                raise forms.ValidationError('Identity mismatch. Identity number must match the confirmation field.')
        # consent cannot be submitted if answer is none to last four consent questions
        if not cleaned_data.get('consent_reviewed', None) or cleaned_data.get('consent_reviewed', None) == 'No':
            raise forms.ValidationError('If consent reviewed is No, patient cannot be enrolled')
        if not cleaned_data.get('study_questions', None) or cleaned_data.get('study_questions', None) == 'No':
            raise forms.ValidationError('If unable to answer questions from client and/or None, patient cannot be enrolled')
        if 'assessment_score' in cleaned_data:
            if not cleaned_data.get('assessment_score', None) or cleaned_data.get('assessment_score', None) == 'No':
                raise forms.ValidationError('Client assessment should at least be a passing score. If No, patient cannot be enrolled')
        if not self.accepted_consent_copy(cleaned_data):
            raise forms.ValidationError('If patient has not been given consent copy and/or None, patient cannot be enrolled')

        if cleaned_data.get('is_literate', None) == 'No' and not cleaned_data.get('witness_name', None):
            raise forms.ValidationError('You wrote subject is illiterate. Please provide the name of a witness here and with signature on the paper document.')
        if cleaned_data.get('is_literate') == 'Yes' and cleaned_data.get('witness_name', None):
            raise forms.ValidationError('You wrote subject is literate. The name of a witness is NOT required.')
        # Always return the full collection of cleaned data.
        return super(BaseSubjectConsentForm, self).clean()

    def accepted_consent_copy(self, cleaned_data):
        if not cleaned_data.get('consent_copy', None) or cleaned_data.get('consent_copy', None) == 'No':
            return False
        else:
            return True
