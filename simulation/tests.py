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
        self.calculation2D = Calculation().read(path)
        self.calculation2D.create_all(path)

    def test_dimenstion(self):
        self.assertEquals(self.calculation2D.dimension, 2)

    def test_natoms(self):
        self.assertEquals(self.calculation2D.natoms,16)

    def test_energy(self):
        self.assertEquals(self.calculation2D.energy,-102.1843278)

    def test_energy_pa(self):
        self.assertEquals((self.calculation2D.energy_pa, -6.3865204875))

    def test_magmom(self):
        self.assertEquals(self.calculation2D.magmom, 11.9998855)

    def test_bandgap(self):
        self.assertEquals(self.calculation2D.band_gap, 1.0072)

