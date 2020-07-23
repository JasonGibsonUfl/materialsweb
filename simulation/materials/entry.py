# simulation/materials/entry.py

from datetime import datetime
import time
import os

from django.db import models
from django.db import transaction
import networkx as nx
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns
from simulation.custom import *
from simulation.materials.composition import *
from simulation.materials.element import Element, Species
from simulation.materials.structure import Structure, StructureError
from simulation.utils import *
# from simulation.computing.resources import Project
from simulation.data.meta_data import *
import simulation.io as io
# import simulation.computing.scripts as scripts
import simulation.analysis.vasp as vasp
import simulation

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

k_desc = 'Descriptive keyword for looking up entries'
h_desc = 'A note indicating a reason the entry should not be calculated'


@add_meta_data('keyword', description=k_desc)
@add_meta_data('hold', description=h_desc)
class Entry(models.Model):
    """Base class for a database entry.
    The core model for typical database entries. An Entry model represents an
    input structure to the database, and can be created from any input file.
    The Entry also ties together all of the associated :mod:`simulation.Structure`,
    :mod:`simulation.Calculation`, :mod:`simulation.Reference`,
    :mod:`simulation.FormationEnergies`, and other associated databas entries.
    Relationships:
        | :mod:`~simulation.Calculation` via calculation_set
        | :mod:`~simulation.DOS` via dos_set
        | :mod:`~simulation.Entry` via duplicate_of
        | :mod:`~simulation.Entry` via duplicates
        | :mod:`~simulation.Element` via element_set
        | :mod:`~simulation.FormationEnergy` via formationenergy_set
        | :mod:`~simulation.Job` via job_set
        | :mod:`~simulation.MetaData` via meta_data
        | :mod:`~simulation.Project` via project_set
        | :mod:`~simulation.Species` via species_set
        | :mod:`~simulation.Structure` via structure_set
        | :mod:`~simulation.Task` via task_set
        | :mod:`~simulation.Reference` via reference
        | :mod:`~simulation.Composition` via composition
    Attributes:
        | id: Primary key (auto-incrementing int)
        | label: An identifying name for the structure. e.g. icsd-1001 or A3
    """
    ### structure properties
    path = models.CharField(max_length=255, unique=True)
    #meta_data = models.ManyToManyField('MetaData')
    label = models.CharField(max_length=20, null=True)

    ### record keeping
    duplicate_of = models.ForeignKey('Entry', related_name='duplicates',
                                     null=True, on_delete=models.CASCADE, )
    ntypes = models.IntegerField(blank=True, null=True)
    natoms = models.IntegerField(blank=True, null=True)

    ### links
    element_set = models.ManyToManyField('Element')
    species_set = models.ManyToManyField('Species')
    composition = models.ForeignKey('Composition', blank=True, null=True, on_delete=models.CASCADE, )

    class Meta:
        app_label = 'simulation'
        db_table = 'entries'

    def __str__(self):
        return '%s - %s' % (self.id, self.name)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Saves the Entry, as well as all associated objects."""
        super(Entry, self).save(*args, **kwargs)
        if not self.duplicate_of:
            self.duplicate_of = self
            super(Entry, self).save(*args, **kwargs)
        if self._structures:
            for k, v in self.structures.items():
                print(v)
                print(k)
                v.label = k
                v.entry = self
                v.save()
        if self._calculations:
            for k, v in self.calculations.items():
                v.label = k
                v.entry = self
                v.save()
        if self._elements:
            self.element_set.set(self.elements)
        if self._species:
            self.species_set.set(self.species)
        if self._keywords or self._holds:
            self.meta_data = self.hold_objects + self.keyword_objects
        self.label = 'hold'

    @staticmethod
    def create(source, keywords=[], **kwargs):
        """
        Attempts to create an Entry object from a provided input file.

        Processed in the following way:

        #. If an Entry exists at the specified path, returns that Entry.
        #. Create an Entry, and assign all fundamental attributes. (natoms,
           ntypes, input, path, elements, keywords, projects).
        #. If the input file is a CIF, and because CIF files have additional
           composition and reference information, if that file format is
           found, an additional test is performed to check that the reported
           composition matches the composition of the resulting structure. The
           reference for the work is also created and assigned to the entry.
        #. Attempt to identify another entry that this is either exactly
           equivalent to, or a defect cell of.

        Keywords:
            keywords: list of keywords to associate with the entry.
            projects: list of project names to associate with the entry.

        """
        source_file = os.path.abspath(source)
        path = os.path.dirname(source_file)

        # Step 1
        if Entry.objects.filter(path=path).exists():
            return Entry.objects.get(path=path)

        # Step 2
        entry = Entry(**kwargs)
        try:
            structure = io.poscar.read(source_file)
            print('read')
        except ValueError:
            structure = io.cif.read(source_file)
        structure.make_primitive()
        entry.source_file = source_file
        entry.path = os.path.dirname(source_file)
        entry.input = structure
        entry.ntypes = structure.ntypes
        entry.natoms = len(structure.sites)
        entry.elements = entry.comp.keys()
        entry.composition = Composition.get(structure.comp)
        #######
        p = path.split('/')
        entry.label = p[-1]
        del p[-1]
        p = '/'.join(p)
        for kw in keywords:
            entry.add_keyword(kw)

        # Step 3
        c1 = structure.composition
        if 'cif' in source_file:
            c2 = structure.reported_composition
            if not c1.compare(c2, 5e-2):
                entry.add_hold("composition mismatch in cif")
                entry.composition = c2
            entry.reference = io.cif.read_reference(source_file)

        # check for perfect crystals
        if not any([s.partial for s in structure.sites]):
            dup = Entry.get(structure)
            if dup is not None:
                entry.duplicate_of = dup
                entry.add_hold('duplicate')
            return entry

        # detect solid solution
        if all([s.occupancy > 0.99 for s in structure.sites]):
            if any([len(s) > 1 for s in structure.sites]):
                entry.add_keyword('solid solution')
        if any([s.partial for s in structure.sites]):
            entry.add_hold('partial occupancy')

        return entry

    @staticmethod
    def get(structure, tol=1e-1):
        if isinstance(structure, Structure):
            return Entry.search_by_structure(structure, tol=tol)


    @staticmethod
    def search_by_structure(structure, tol=1e-2):
        c = Composition.get(structure.comp)
        for e in c.entries:
            if e.structure.compare(structure, tol=tol):
                return e
        return None
    _elements = None

    @property
    def elements(self):
        """List of Elements"""
        if self._elements is None:
            self._elements = [Element.get(e) for e in self.comp.keys()]
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = [Element.get(e) for e in elements]

    _species = None

    @property
    def species(self):
        """List of Species"""
        if self._species is None:
            self._species = [Species.get(s) for s in self.spec_comp.keys()]
        return self._species

    @species.setter
    def species(self, species):
        self._species = [Species.get(e) for e in species]


    _structures = None

    @property
    def structures(self):
        if self._structures is None:
            if self.id is None:
                self._structures = {}
            else:
                structs = {}
                for s in self.structure_set.exclude(label=''):
                    structs[s.label] = s
                self._structures = structs
        return self._structures

    s = structures

    @structures.setter
    def structures(self, structs):
        if not isinstance(structs, dict):
            raise TypeError('structures must be a dict')
        if not all(isinstance(v, Structure) for v in structs.values()):
            raise TypeError('structures must be a dict of Calculations')
        self._structures = structs

    @structures.deleter
    def structures(self, struct):
        self._structures[struct].delete()
        del self._structures[struct]

    _calculations = None

    @property
    def calculations(self):
        """Dictionary of label:Calculation pairs."""
        if self._calculations is None:
            if self.id is None:
                self._calculations = {}
            else:
                calcs = {}
                for c in self.calculation_set.exclude(label=''):
                    calcs[c.label] = c
                self._calculations = calcs
        return self._calculations

    c = calculations

    @calculations.setter
    def calculations(self, calcs):
        if not isinstance(calcs, dict):
            raise TypeError('calculations must be a dict')
        if not all(isinstance(v, vasp.Calculation) for v in calcs.values()):
            raise TypeError('calculations must be a dict of Calculations')
        self._calculations = calcs

    @calculations.deleter
    def calculations(self, calc):
        self._calculations[calc].delete()
        del self._calculations[calc]

    @property
    def input(self):
        return self.structures.get('input')

    @property
    def structure(self):
        try:
            return self.structures[self.label]
        except KeyError:
            return None

    @input.setter
    def input(self, structure):
        self.structures['input'] = structure

    @property
    def comp(self):
        if not self.composition_id is None:
            return parse_comp(self.composition_id)
        elif not self.input is None:
            return self.input.comp
        else:
            return {}

    @property
    def spec_comp(self):
        """
        Composition dictionary, using species (element + oxidation state)
        instead of just the elements.

        """
        if self.input is None:
            return {}
        else:
            return self.input.spec_comp

    @property
    def unit_comp(self):
        """Composition dictionary, normalized to 1 atom."""
        return unit_comp(self.comp)

    @property
    def red_comp(self):
        """Composition dictionary, in reduced form."""
        return reduce_comp(self.comp)

    @property
    def name(self):
        """Unformatted name"""
        return format_comp(reduce_comp(self.comp))

    @property
    def latex(self):
        """LaTeX formatted name"""
        return format_latex(reduce_comp(self.comp))

    @property
    def html(self):
        """HTML formatted name"""
        return format_html(reduce_comp(self.comp))

    @property
    def proto_label(self):
        # if not self.prototype is None:
        #    return self.prototype.name
        protos = []
        for e in self.duplicates.all():
            if not e.prototype is None:
                protos.append(e.prototype.name)

        protos = list(set(protos))
        if len(protos) == 1:
            return protos[0]
        else:
            return ', '.join(protos)

    @property
    def space(self):
        """Return the set of elements in the input structure.

        Examples::

            >>> e = Entry.create("fe2o3/POSCAR") # an input containing Fe2O3
            >>> e.space
            set(["Fe", "O"])

        """
        return set([e.symbol for e in self.elements])

    @property
    def spacegroup(self):
        return self.structure.spacegroup

    def visualize(self, structure='source'):
        """Attempts to open the input structure for visualization using VESTA"""
        os.system('VESTA %s/POSCAR' % self.path)
