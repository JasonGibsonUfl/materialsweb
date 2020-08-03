from django.db import models
from simulation.custom import DictField, NumpyArrayField
from pymatgen.core.structure import Structure


class PyStructure(models.Model):

    entry = models.ForeignKey('Entry', null=True, on_delete=models.CASCADE,),
    element_set = models.ManyToManyField('Element')
    label = models.CharField(blank=True, max_length=63)
    composition = models.ForeignKey('Composition', null=True, related_name='structure_set', on_delete=models.CASCADE,)
    
    structure = DictField(blank=True, null=True)
    #sites = DictField(blank=True, null=True)

    def read(self,fileName = 'POSCAR'):
        file1 = open(fileName, 'r')
        Lines = file1.readlines()
        poscar = ''
        for Line in Lines:
            poscar += Line

        s = Structure.from_str(poscar, fmt='poscar').as_dict()
        self.structure = s



