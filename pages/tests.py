from django.test import TestCase
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time
# Create your tests here.
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

class TestMaterialswebHome(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('/home/cobra_commander/.wdm/drivers/chromedriver/linux64/83.0.4103.39/chromedriver')

        #self.browser = webdriver.Chrome(ChromeDriverManager().install())

        #self.browser = webdriver.Chrome('./chromedriver')

    def tearDown(self):
        self.browser.close()

    def test_no_projects_alerts_is_displated(self):
        self.browser.get('https://www.google.com/')#self.live_server_url)
        #time.sleep(50)
