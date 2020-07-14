from django.test import TestCase
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# Create your tests here.

class TestMaterialswebHome(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('./chromedriver')

    def test_foo(self):
        self.assertEquals(0,1)