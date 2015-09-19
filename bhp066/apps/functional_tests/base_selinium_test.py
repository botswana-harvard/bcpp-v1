from selenium import webdriver

from django.contrib.auth.models import User

from .pages.login_page import LoginPage
from apps.bcpp_household.tests.factories import PlotFactory
import unittest


class BaseSeleniumTest(unittest.TestCase):

    username = 'testuser'
    password = '12345'
    email = 'testuser@123.org'
    app_label = 'bcpp_subject'
    community = 'otse'

    def setUp(self):
        User.objects.create_superuser(self.username, self.email, self.password)
        # super().setUp()
        self.browser = webdriver.Firefox()
        self.plot = PlotFactory(community=self.community, household_count=1, status='residential_habitable', plot_identifier='400007-03')

    def tearDown(self):
        self.plot.delete()
        self.browser.close()

    def login(self):
        self.login_page = LoginPage(self.browser)
        self.login_page.login(self.username, self.password)
