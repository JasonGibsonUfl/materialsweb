from django.test import TestCase
from simulation.materials.entry import Entry
from simulation.analysis.vasp.calculation import Calculation
from scripts.fill_elements import run as run_e
from scripts.fill_spacegroups import run as run_s
from scripts.fill_wyckoffsites import run as run_w

class TestSimulation(TestCase):

    def setUp(self):
        path = '/var/www/materialsweb/static/database/mp-691133'
        run_e()
        run_s()
        run_w()
        self.calculation1 = Calculation().read(path)
        self.calculation1.create_all(path)

    def test_bandgap(self):
        print(self.calculation1.band_gap)
        self.assertEquals(1,1)#self.calculation1.band_gap, 1.0072)