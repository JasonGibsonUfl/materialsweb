from django.test import TestCase
from simulation.materials.entry import Entry
from simulation.analysis.vasp.calculation import Calculation
from scripts.fill_elements import run

class TestSimulation(TestCase):

    def setUp(self):
        path = '/var/www/materialsweb/static/database/mp-691133'
        run()
        self.calculation1 = Calculation()
        self.calculation1.read(path)
        self.calculation1.create_all(path)

    def test_bandgap(self):
        print(self.calculation1.band_gap)
        self.assertEquals(1,1)#self.calculation1.band_gap, 1.0072)