from django.test import TestCase
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# Create your tests here.

class TestMaterialswebHome(StaticLiveServerTestCase):

    def test_foo(self):
        self.assertEquals(0,1)