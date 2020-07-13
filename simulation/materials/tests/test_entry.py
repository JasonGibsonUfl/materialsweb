from django.test import TestCase
from simulation.materials.entry import Entry
from simulation.analysis.vasp

class TestEntry(TestCase):

    def setUp(self):
        self.entry1 =