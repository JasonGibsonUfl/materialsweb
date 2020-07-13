from django.test import TestCase
from simulation.materials.entry import Entry
from simulation.analysis.vasp.calculation import Calculation
from scripts.fill_elements import run as run_e
from scripts.fill_spacegroups import run as run_s
from scripts.fill_wyckoffsites import run as run_w

run_e()
run_s()
run_w()
class TestSimulation(TestCase):

    def setUp(self):
        #run_e()
        #run_s()
        #run_w()
        path = '/var/www/materialsweb/static/database/mp-691133'

        self.calculation2D = Calculation().read(path)
        self.calculation2D.create_all(path)

    def test_calculation(self):
        '''Calcualtion quantities'''
        self.assertEquals(self.calculation2D.dimension, 2)
        self.assertEquals(self.calculation2D.natoms,16)
        self.assertEquals(self.calculation2D.energy,-102.1843278)
        self.assertEquals(self.calculation2D.energy_pa, -6.3865204875)
        self.assertEquals(self.calculation2D.magmom, 11.9998855)
        self.assertEquals(self.calculation2D.magmom_pa, 0.74999284375)
        self.assertEquals(self.calculation2D.band_gap, 1.0072)
        self.assertEquals(self.calculation2D.formation_energy, 179)




'''
    def test_dimenstion(self):
        self.assertEquals(self.calculation2D.dimension, 2)

    def test_natoms(self):
        self.assertEquals(self.calculation2D.natoms,16)

    def test_energy(self):
        self.assertEquals(self.calculation2D.energy,-102.1843278)

    def test_energy_pa(self):
        self.assertEquals(self.calculation2D.energy_pa, -6.3865204875)

    def test_magmom(self):
        self.assertEquals(self.calculation2D.magmom, 11.9998855)

    def test_magmom_pa(self):
        self.assertEquals(self.calculation2D.magmom_pa, 0.74999284375)

    def test_bandgap(self):
        self.assertEquals(self.calculation2D.band_gap, 1.0072)

    def formation_energy(self):
'''
