from django.test import TestCase
from simulation.materials.entry import Entry
from simulation.analysis.vasp.calculation import Calculation
from scripts.fill_elements import run as run_e
from scripts.fill_spacegroups import run as run_s
from scripts.fill_wyckoffsites import run as run_w

class TestSimulation(TestCase):

    def setUp(self):
        run_e()
        run_s()
        run_w()
        path2D = '/var/www/materialsweb/static/database/mp-691133'

        self.calculation2D = Calculation().read(path2D)
        self.calculation2D.create_all(path2D)
        self.entry2D = self.calculation2D.entry
        self.composition2D = self.entry2D.composition

        path3D = '/var/www/materialsweb/static/database/MAX_phases/all_competitors/mp-867780'

        self.calculation3D = Calculation().read(path3D)
        self.calculation3D.create_all(path3D)
        self.entry3D = self.calculation3D.entry
        self.composition3D = self.entry3D.composition

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
        '''Entry Quantities'''
        self.assertEquals(self.entry2D.natoms, 16)
        '''Compostion quantities'''
        self.assertEquals(self.composition2D.mass, 21.250710427785002)
        self.assertEquals(self.composition2D.formula, 'Cr1 H1 O2')
        self.assertEquals(self.composition2D.generic, 'ABC2')
        self.assertEquals(self.composition2D.element_list, 'Cr_H_O_')

        '''Calcualtion quantities'''
        self.assertEquals(self.calculation3D.dimension, 3)
        self.assertEquals(self.calculation3D.natoms,4)
        self.assertEquals(self.calculation3D.energy,-21.42383041)
        self.assertEquals(self.calculation3D.energy_pa, -5.3559576025)
        self.assertEquals(self.calculation3D.magmom, 1.1246361)
        self.assertEquals(self.calculation3D.magmom_pa, 0.281159025)
        self.assertEquals(self.calculation3D.band_gap, 0)
        '''Entry Quantities'''
        self.assertEquals(self.entry3D.natoms, 4)
        '''Compostion quantities'''
        self.assertEquals(self.composition3D.mass, 33.23515081405)
        self.assertEquals(self.composition3D.formula, 'Al3 Cr1')
        self.assertEquals(self.composition3D.generic, 'AB3')
        self.assertEquals(self.composition3D.element_list, 'Al_Cr_')
        
        ml_list =[3.8536327377042804e-05, 3.853628381808742e-05, 3.853628381808746e-05, 3.853632737704282e-05, 3.953138878697092e-05, 3.9531390956468254e-05, 3.953138878697098e-05, 3.953139095646848e-05, 3.5848701044293688e-06, 4.451154568298833e-05, 3.584870104429372e-06, 3.5848789431573475e-06, 4.4511563103682824e-05, 4.451154568298852e-05, 3.5848789431573623e-06, 4.4511563103683095e-05]
        self.assertEquals(self.calculation2D.get_symmetry_functions_g2(), ml_list)