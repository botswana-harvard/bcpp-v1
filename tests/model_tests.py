import re
from django.test import TestCase
from django.conf import settings
from bhp_registration.tests.factories import RegisteredSubjectFactory
from bhp_registration.models import RegisteredSubject
from bhp_consent.models import TestSubjectConsent
from bhp_consent.tests.factories import TestSubjectConsentFactory
from bhp_identifier.exceptions import IdentifierError


class ModelTests(TestCase):

    def test_p1(self):
        """Tests the subject_identifier is a uuid by default"""
        print 'test subject_identifier is uuid by default'
        registered_subject = RegisteredSubjectFactory()
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        self.assertTrue(re_pk.match(registered_subject.subject_identifier))

    def test_p2(self):
        """Tests natural key."""
        re_pk = re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}')
        for cls_tpl in [(RegisteredSubject, RegisteredSubjectFactory), (TestSubjectConsent, TestSubjectConsentFactory)]:
            cls, cls_factory = cls_tpl
            print 'using {0}'.format(cls._meta.object_name)
            print 'test {0} natural key'.format(cls._meta.object_name)
            rs = cls_factory()
            rs2 = cls.objects.get_by_natural_key(rs.subject_identifier)
            self.assertEqual(rs, rs2)
            args = rs.natural_key()
            rs3 = cls.objects.get_by_natural_key(*args)
            self.assertEqual(rs, rs3)
            print 'test {0} does not change subject identifier on save of exisiting instance'.format(cls._meta.object_name)
            rs = cls_factory()
            old_identifier = rs.subject_identifier
            rs.subject_identifier = 'TEST_IDENTIFIER'
            self.assertRaises(IdentifierError, rs.save)
            rs = cls.objects.get(pk=rs.pk)
            self.assertEqual(old_identifier, rs.subject_identifier)
            if rs.get_user_provided_subject_identifier_attrname():
                print 'test {0} uses user provided subject identifier'.format(cls._meta.object_name)
                rs = cls_factory(**{rs.get_user_provided_subject_identifier_attrname(): 'TEST_IDENTIFIER'})
                rs = cls.objects.get(pk=rs.pk)
                self.assertEqual(rs.subject_identifier, 'TEST_IDENTIFIER')
            else:
                rs = cls_factory(subject_identifier='TEST_IDENTIFIER')
            print 'test {0} raises error if duplicate subject_identifier'.format(cls._meta.object_name)
            rs = cls.objects.get(subject_identifier='TEST_IDENTIFIER')
            self.assertRaises(IdentifierError, cls_factory, subject_identifier='TEST_IDENTIFIER')
            print 'test {0} assigns uuid or study identifier if blank subject_identifier'.format(cls._meta.object_name)
            rs = cls_factory(subject_identifier=None)
            self.assertIsNotNone(rs.subject_identifier)
            if issubclass(cls, RegisteredSubject):
                self.assertTrue(re_pk.match(rs.subject_identifier))
            if issubclass(cls, TestSubjectConsent):
                self.assertTrue(rs.subject_identifier.startswith(settings.PROJECT_IDENTIFIER_PREFIX))
            print 'test {0} unicode is masked if subject identifier is a uuid'.format(cls._meta.object_name)
            rs = cls_factory()
            if re_pk.match(rs.subject_identifier):
                self.assertTrue('identifier not set' in unicode(rs))
            else:
                self.assertFalse('identifier not set' in unicode(rs))

