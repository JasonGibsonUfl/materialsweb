from django.test import TestCase
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import time
# Create your tests here.

class TestMaterialswebHome(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox('/var/www/materialsweb/pages/drivers', executable_path= '/var/www/materialsweb/pages/firefox.sh')

    def tearDown(self):
        self.browser.close()

    def test_no_projects_alerts_is_displated(self):
        self.browser.get(self.live_server_url)
        time.sleep(20)
