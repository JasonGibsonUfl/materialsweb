# simulation/materials/structure.py

"""
The Structure class is used to represent a crystal structure.
"""
import os
import numpy as np
import numpy.linalg as la
import time
import copy
import pprint
import random
import subprocess
from collections import defaultdict
import logging

from django.db import models
from django.db import transaction


from pymatgen.core.structure import Structure as StructureP

from .element import Element, Species
from simulation.materials.atom import Atom, Site
from .composition import Composition
from simulation.utils.strings import format_comp, parse_comp, reduce_comp
from simulation.utils.math_tool import *
from simulation.data.meta_data import *
from simulation.analysis.symmetry.routines import get_symmetry_dataset
from simulation.analysis.symmetry.routines import find_primitive
from simulation.analysis.symmetry.spacegroup import Spacegroup
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)

class StructureError(Exception):
    """Structure related problem"""

class TMKPointsError(Exception):
    """Problem with TM k-points generation"""

class Structure(models.Model, object):
    """
    Structure model. Principal attributes are a lattice and basis set.
    Relationships:
        | :mod:`~simulation.Entry` via entry
        | :mod:`~simulation.Atom` via atom_set: Atoms in the structure. More commonly
        |   handled by the managed attributed `atoms`.
        | :mod:`~simulation.Calculation` via calculated. Calculation objects
        |   that the structure is an *output* from.
        | :mod:`~simulation.Calculation` via calculation_set. Returns calculation
        |   objects that the structure is an *input* to.
        | :mod:`~simulation.Composition` via composition.
        | :mod:`~simulation.Element` via element_set
        | :mod:`~simulation.Spacegroup` via spacegroup
        | :mod:`~simulation.Species` via species_set
        | :mod:`~simulation.Reference` Original literature reference.
        | :mod:`~simulation.MetaData` via meta_data
    Attributes:
        | **Identification**
        | id
        | label: key in the Entry.structures dictionary.
        | natoms: Number of atoms.
        | nsites: Number of sites.
        | ntypes: Number of elements.
        | measured: Experimentally measured structure?
        | source: Name for source.
        |
        | **Lattice**
        | x1, x2, x3
        | y1, y2, y3
        | z1, z2, z3: Lattice vectors of the cell. Accessed via `cell`.
        | volume
        | volume_pa
        |
        | **Calculated properties**
        | delta_e: Formation energy (eV/atom)
        | meta_stability: Distance from the convex hull (eV/atom)
        | energy: Total DFT energy (eV/FU)
        | energy_pa: Total DFT energy (eV/atom)
        | magmom: Total magnetic moment (&Mu;<sub>b</sub>)
        | magmom_pa: Magnetic moment per atom.
        | sxx, sxy, syy
        | syx, szx, szz: Stresses on the cell. Accessed via `stresses`.
    Examples::
        >>> s = io.read(INSTALL_PATH+'/io/files/POSCAR_FCC')
        >>> s.atoms
        >>> s.cell
        >>> s.magmoms
        >>> s.forces
        >>> s.stresses
    """
    entry = models.ForeignKey('Entry', null=True, on_delete=models.CASCADE,)
    element_set = models.ManyToManyField('Element')
    species_set = models.ManyToManyField('Species')
    meta_data = models.ManyToManyField('MetaData')
    label = models.CharField(blank=True, max_length=63)
    measured = models.BooleanField(default=False)

    composition = models.ForeignKey('Composition', null=True, related_name='structure_set', on_delete=models.CASCADE,)
    natoms = models.IntegerField(null=True, blank=True)
    nsites = models.IntegerField(null=True, blank=True)
    ntypes = models.IntegerField(null=True, blank=True)

    x1 = models.FloatField()
    x2 = models.FloatField()
    x3 = models.FloatField()
    y1 = models.FloatField()
    y2 = models.FloatField()
    y3 = models.FloatField()
    z1 = models.FloatField()
    z2 = models.FloatField()
    z3 = models.FloatField()

    volume = models.FloatField(blank=True, null=True)
    volume_pa = models.FloatField(blank=True, null=True)

    sxx = models.FloatField(default=0)
    syy = models.FloatField(default=0)
    szz = models.FloatField(default=0)
    sxy = models.FloatField(default=0)
    syz = models.FloatField(default=0)
    szx = models.FloatField(default=0)

    spacegroup = models.ForeignKey('Spacegroup', blank=True,
            null=True, on_delete=models.CASCADE,)

    energy = models.FloatField(blank=True, null=True)
    energy_pa = models.FloatField(blank=True, null=True)
    magmom = models.FloatField(blank=True, null=True)
    magmom_pa = models.FloatField(blank=True, null=True)
    delta_e = models.FloatField(blank=True, null=True)
    meta_stability = models.FloatField(blank=True, null=True)

    _reciprocal_lattice = None
    _distinct_atoms = []
    _magmoms = []

    class Meta:
        app_label = 'simulation'
        db_table = 'structures'
        unique_together = ('entry', 'label')
        
    def __eq__(self, other):
        return self.compare(other)

    def __str__(self):
        return format_comp(reduce_comp(self.comp))

    def printf(self):
        res = format_comp(reduce_comp(self.comp)) + '\n'
        res += self.lat_param_string()
        for i, s in enumerate(self.sites):
            res += '\n - %s' % s
            if i == 6:
                res += '\n ... \n %d more atoms.' % (len(self) - 6)
                break
        return res

    def __getitem__(self, i):
        return self.atoms[i]

    def __len__(self):
        return len(self.atoms)



    def get_jmol2(self):
        from pymatgen.core.operations import SymmOp
        needs_shift = False
        structure = StructureP.from_file(self.entry.path+'/POSCAR')
        if structure.lattice.a == max(structure.lattice.abc):
            translation = SymmOp.from_rotation_and_translation(translation_vec=(structure.lattice.a / 2, 0, 0))
            for site in structure.sites:
                if site._frac_coords[0] > 0.9 or site._frac_coords[0] < 0.1:
                    needs_shift = True
            if needs_shift:
                structure.apply_operation(translation)
            structure.make_supercell([1, 6, 6])
        elif structure.lattice.b == max(structure.lattice.abc):
            translation = SymmOp.from_rotation_and_translation(translation_vec=(0, structure.lattice.b / 2, 0))
            for site in structure.sites:
                if site._coords[1] > 0.9 or site._coords[1] < 0.1:
                    needs_shift = True
            if needs_shift:
                structure.apply_operation(translation)
            structure.make_supercell([6, 1, 6])
        else:
            translation = SymmOp.from_rotation_and_translation(translation_vec=(0, 0, structure.lattice.c / 2))
            for site in structure.sites:
                if site._frac_coords[2] > 0.9 or site._frac_coords[2] < 0.1:
                    needs_shift = True
            if needs_shift:
                structure.apply_operation(translation)

            structure.make_supercell([6, 6, 1])
            print('frac_coord: '+ str(site._frac_coords[2]))

        print(structure.lattice.b)
        xyz_structure = [str(structure.num_sites),structure.composition.reduced_formula]
        for site in structure.sites:
            element = site._species.reduced_formula.replace('2', '')
            atom = '{} {} {} {}'.format(element, str(site.x), str(site.y),str(site.z))
            xyz_structure.append(atom)
        #return '+'.join(xyz_structure)
        string = str(xyz_structure)
        string = string.replace('[', '')
        string = string.replace(']', '')
        string = string.replace(', ', r'\n')
        string = string.replace("'", "")
        return string

    def get_jmol3(self):
        from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
        structure = StructureP.from_file(self.entry.path + '/POSCAR')
        analyzer = SpacegroupAnalyzer(structure)
        structure = analyzer.get_refined_structure()
        structure.make_supercell([2, 2, 2])
        xyz_structure = [str(structure.num_sites),structure.composition.reduced_formula]
        for site in structure.sites:
            element = site._species.reduced_formula.replace('2', '')
            atom = '{} {} {} {}'.format(element, str(site.x), str(site.y),str(site.z))
            xyz_structure.append(atom)
        string = str(xyz_structure)
        string = string.replace('[', '')
        string = string.replace(']', '')
        string = string.replace(', ', r'\n')
        string = string.replace("'", "")
        return string

    @staticmethod
    def create(cell, atoms=[], **kwargs):
        """
        Creates a new Structure.

        Arguments:
            cell: 3x3 lattice vector array

        Keyword Arguments:
            atoms: List of ``Atom`` creation arguments. Can be a list of
            [element, coord], or a list of [element, coord, kwargs].

        Examples::

            >>> a = 3.54
            >>> cell = [[a,0,0],[0,a,0],[0,0,a]]
            >>> atoms = [('Cu', [0,0,0]),
                         ('Cu', [0.5, 0.5, 0.5])]
            >>> s = Structure.create(cell, atoms)
            >>> atoms = [('Cu', [0,0,0], {'magmom':3}),
                    ('Cu', [0.5, 0.5, 0.5], {'magmom':-3})]
            >>> s2 = Structure.create(cell, atoms)

        """
        s = Structure(**kwargs)
        if np.shape(cell) == (6,):
            s.lat_params = cell
        elif np.shape(cell) == (3, 3):
            s.cell = cell
        elif np.shape(cell) == (3,):
            s.cell = np.eye(3) * cell

        for atom in atoms:
            if len(atom) == 2:
                atom = Atom.create(*atom)
            elif len(atom) == 3:
                atom = Atom.create(atom[0], atom[1], **atom[2])
            s.add_atom(atom)

        if s.comp:
            s.composition = Composition.get(s.comp)

        return s

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.composition:
            self.composition = Composition.get(self.comp)

        self.natoms = len(self.atoms)
        self.nsites = len(self.sites)
        self.ntypes = len(self.comp.keys())
        self.get_volume()

        super(Structure, self).save(*args, **kwargs)

        self.element_set.set(self.elements)
        self.species_set.set(self.species)
        #self.meta_data = self.comment_objects + self.keyword_objects

        if not self._sites is None:
            for s in self.sites:
                if not s.id:
                    s.save()
                self.site_set.add(s)
        if not self._atoms is None:
            for a in self.atoms:
                if not a.id:
                    a.save()
                self.atom_set.add(a)
        super(Structure, self).save(*args, **kwargs)

        if not self.spacegroup:
            self.symmetrize()

    _atoms = None

    @property
    def atoms(self):
        """
        List of ``Atoms`` in the structure.
        """
        if self._atoms is None:
            if not self.id:
                self._atoms = []
            else:
                self._atoms = list(self.atom_set.all())
                self._sites = list(self.site_set.all())
        return self._atoms

    @atoms.setter
    def atoms(self, atoms):
        self._atoms = []
        self._sites = []
        for a in atoms:
            self.add_atom(a)
        self.natoms = len(self._atoms)
        self.ntypes = len(self.comp)

    _abc = None

    @property
    def atoms_by_coord(self):
        if self._abc is None:
            _abc = {}
            for a in self.atoms:
                _abc[tuple(a.cart_coord.tolist())] = a
            self._abc = _abc
        return self._abc

    _sbc = None

    @property
    def sites_by_coord(self):
        if self._sbc is None:
            _sbc = {}
            for s in self.sites:
                _sbc[tuple(s.cart_coord.tolist())] = s
            self._sbc = _sbc
        return self._sbc

    _sites = None

    @property
    def sites(self):
        """
        List of ``Sites`` in the structure.
        """
        if self._sites is None:
            self.atoms
            self.get_sites()
            self.nsites = len(self.sites)
        return self._sites

    @sites.setter
    def sites(self, sites):
        self._atoms = []
        for s in sites:
            self.add_site(s)
        self._sites = sites
        self.natoms = len(self.atoms)
        self.ntypes = len(self.comp)

    @property
    def site_compositions(self):
        return [format_comp(s.comp) for s in self.sites]

    @site_compositions.setter
    def site_compositions(self, values):
        atoms = []
        for s, v in zip(self.sites, values):
            s.comp = parse_comp(v)
            atoms += s.atoms
        self._atoms = atoms
        self.natoms = len(atoms)

    @property
    def site_comp_indices(self):
        """
        List of site compositions, length equal to number of sites, each
        unique site composition identified by an integer.
        """
        return np.unique(self.site_compositions, return_inverse=True)[-1]

    @property
    def elements(self):
        """List of Elements"""
        return [Element.get(e) for e in self.comp.keys()]

    @property
    def species(self):
        """List of species"""
        return [Species.get(s) for s in self.spec_comp.keys()]

    @property
    def stresses(self):
        """Calculated stresses, a numpy.ndarray of shape (6,)"""
        return np.array([self.sxx, self.syy, self.szz,
                         self.sxy, self.syz, self.szx])

    @stresses.setter
    def stresses(self, vector):
        vector = [x for x in vector]

        self.sxx, self.syy, self.szz = vector[0:3]
        self.sxy, self.syz, self.szx = vector[3:6]

    def get_volume(self):
        """Calculates the volume from the triple product of self.cell"""
        b1, b2, b3 = self.cell
        self.volume = abs(np.dot(np.cross(b1, b2), b3))
        self.volume_pa = self.volume / len(self)
        return self.volume

    def set_label(self, label):
        self.label = label
        if not self.entry is None:
            self.entry.structures[label] = self
        # if self.id:
        #    Structure.objects.filter(id=self.id).update(label=label)

    def set_volume(self, value):
        """
        Rescales the unit cell to the specified volume, keeping the direction
        and relative magnitudes of all lattice vectors the same.
        """
        self.get_volume()
        scale = value / self.volume
        self.cell = self.cell * (scale ** (1 / 3.))
        self.volume_pa = value / self.natoms
        self.volume = value

    def get_volume_sum_of_elements(self):
        volume = 0
        for atom in self:
            volume += atom.element.volume * atom.occupancy
        return volume

    def set_volume_to_sum_of_elements(self):
        volume = 0
        for atom in self:
            volume += atom.element.volume * atom.occupancy
        self.set_volume(volume)

    @property
    def lat_param_dict(self):
        """Dictionary of lattice parameters."""
        return dict(zip(['a', 'b', 'c', 'alpha', 'beta', 'gamma'],
                        self.lat_params))

    _lat_params = None

    @property
    def lat_params(self):
        """Tuple of lattice parameters (a, b, c, alpha, beta, gamma)."""
        if self._lat_params is None:
            self._lat_params = basis_to_latparams(self.cell)
        return self._lat_params

    @lat_params.setter
    def lat_params(self, lat_params):
        self.cell = latparams_to_basis(lat_params)
        self._lat_params = lat_params

    def lat_param_string(self, format='screen'):
        """
        Generates a human friendly representation of the lattice parameters of
        a structure.

        Keyword Arguments:
            format: ('screen'|'html'|'mathtype')

        """
        formats = {
            'html': {
                'keys': ['&alpha;', '&beta;', '&gamma'],
                'newline': '<br>'},
            'mathtype': {
                'keys': [r'\alpha', r'\beta', r'\gamma'],
                'newline': '\n'},
            'screen': {
                'keys': [r'alpha', r'beta', r'gamma'],
                'newline': '\n'}
        }

        f = formats[format]

        lp = self.lat_param_dict
        if abs(lp['a'] - lp['b']) < 1e-4:
            if abs(lp['a'] - lp['c']) < 1e-4:
                lpstr = 'a = b = c = %0.3g' % lp['a']
            else:
                lpstr = 'a = b = %0.3g, c = %0.3g' % (lp['a'], lp['c'])
        else:
            lpstr = 'a = %0.3g, b = %0.3g, c = %0.3g' % (lp['a'], lp['b'], lp['c'])

        lpstr += f['newline']

        if abs(lp['alpha'] - lp['beta']) < 1e-2:
            if abs(lp['alpha'] - lp['gamma']) < 1e-2:
                lpstr += '%s = %s = %s = %0.3g' % (
                    f['keys'][0], f['keys'][1], f['keys'][2], lp['alpha'])
            else:
                lpstr += '%s = %s = %0.3g, %s = %0.3g' % (
                    f['keys'][0], f['keys'][1], lp['alpha'],
                    f['keys'][2], lp['gamma'])
        else:
            print(f['keys'][0])
            print(lp['gamma'])
            lpstr += '&alpha; = %0.3g, &beta; = %0.3g, &gamma; = %0.3g' % (
                float(lp['alpha']),
                float(lp['beta']),
                float(lp['gamma']))
        return lpstr

    lp = lat_params
    _cell = None

    @property
    def cell(self):
        """Lattice vectors, 3x3 numpy.ndarray."""
        if self._cell is None:
            self._cell = np.array([
                [self.x1, self.x2, self.x3],
                [self.y1, self.y2, self.y3],
                [self.z1, self.z2, self.z3]])
        return self._cell

    @cell.setter
    def cell(self, cell):
        self.x1, self.x2, self.x3 = cell[0]
        self.y1, self.y2, self.y3 = cell[1]
        self.z1, self.z2, self.z3 = cell[2]
        self._lat_params = None
        self._inv = None
        self._metrical_matrix = None
        for a in self.atoms:
            a._cart = None
        for s in self.sites:
            s._cart = None
        self._cell = None

    _metrical_matrix = None

    @property
    def metrical_matrix(self):
        """np.dot(self.cell.T, self.cell)"""
        if self._metrical_matrix is None:
            self._metrical_matrix = self.cell.dot(self.cell.T)
        return self._metrical_matrix

    @metrical_matrix.setter
    def metrical_matrix(self, G):
        a = np.sqrt(abs(G[0, 0]))
        b = np.sqrt(abs(G[1, 1]))
        c = np.sqrt(abs(G[2, 2]))
        al = np.arccos(G[1, 2] / abs(b * c)) * 180 / np.pi
        be = np.arccos(G[0, 2] / abs(a * c)) * 180 / np.pi
        ga = np.arccos(G[0, 1] / abs(a * b)) * 180 / np.pi
        self.cell = latparams_to_basis([a, b, c, al, be, ga])

    @property
    def atomic_numbers(self):
        """List of atomic numbers, length equal to number of atoms."""
        return np.array([atom.element.z for atom in self.atoms])

    @property
    def atom_types(self):
        """List of atomic symbols, length equal to number of atoms."""
        return np.array([atom.element_id for atom in self.atoms])

    @atom_types.setter
    def atom_types(self, elements):
        if isinstance(elements, list):
            for a, e in zip(self.atoms, elements):
                a.element_id = e
        elif isinstance(elements, str):
            for a in self.atoms:
                a.element_id = elements
        elif isinstance(elements, simulation.Element):
            for a in self.atoms:
                a.element = elements
        else:
            raise ValueError('Unrecognized type for atom type assignment')

    @property
    def species_types(self):
        """List of species, length equal to number of atoms."""
        return np.array([atom.species for atom in self.atoms])

    @property
    def species_id_types(self):
        """List of species, length equal to number of atoms, each unique species
        identified by an integer.
        """
        return np.unique(self.species_types, return_inverse=True)[-1]

    def symmetrize(self, tol=1e-3, angle_tol=-1):
        """
        Analyze the symmetry of the structure. Uses spglib to find the
        symmetry.

        symmetrize sets:
         * spacegroup -> Spacegroup
         * uniq_sites -> list of unique Sites
         * orbits -> lists of equivalent Atoms
         * rotations -> List of rotation operations
         * translations -> List of translation operations
         * operatiosn -> List of (rotation,translation) pairs
         * for each atom: atom.wyckoff -> WyckoffSite
         * for each site: site.multiplicity -> int

        """
        self.get_sites()
        dataset = get_symmetry_dataset(self, symprec=tol)
        if not dataset:
            return
        self.spacegroup = Spacegroup.objects.get(pk=dataset['number'])
        for i, site in enumerate(self.sites):
            site.wyckoff = self.spacegroup.get_site(dataset['wyckoffs'][i])
            site.structure = self
        counts = defaultdict(int)
        orbits = defaultdict(list)
        origins = {}
        for i, e in enumerate(dataset['equivalent_atoms']):
            counts[e] += 1
            origins[i] = e
            orbits[e].append(self.sites[i])
        self.origins = origins
        self.operations = zip(dataset['rotations'], dataset['translations'])
        rots = []
        for r in dataset['rotations']:
            if not any([np.allclose(r, x) for x in rots]):
                rots.append(r)
        self.rotations = rots
        trans = []
        for t in dataset['translations']:
            if not any([np.allclose(t, x) for x in trans]):
                trans.append(t)
        self.translations = trans
        self.orbits = orbits.values()
        ##self.duplicates = dict((self.sites[e], v) for e, v in orbits.items())
        ## See comment about hashes and Dictionary keys
        self.duplicates = dict((e, v) for e, v in orbits.items())
        self._uniq_sites = []
        self._uniq_atoms = []
        for ind, mult in counts.items():
            site = self.sites[ind]
            for site2 in self.duplicates[ind]:
                site2.multiplicity = mult
            site.index = ind
            site.multiplicity = mult
            self._uniq_sites.append(site)
            for a in site:
                self._uniq_atoms.append(a)

    _uniq_atoms = None

    @property
    def uniq_atoms(self):
        if self._uniq_atoms is None:
            self.symmetrize()
        return self._uniq_atoms

    _uniq_sites = None

    @property
    def uniq_sites(self):
        if self._uniq_sites is None:
            self.symmetrize()
        return self._uniq_sites


    def get_coord(self, vec, wrap=True):
        trans = self.inv.T.dot(vec)
        if wrap:
            return wrap(trans)
        else:
            return trans

    def contains(self, atom, tol=0.01):
        atom.structure = self
        for atom2 in self.atoms:
            atom2.structure = self
            if not atom2.element_id == atom.element_id:
                continue
            if abs(shortest_dist(atom2, self.cell) - shortest_dist(atom, self.cell)) > tol:
                continue
            d = self.get_distance(atom, atom2, limit=1)
            if d is not None:
                if d < tol and not d is None:
                    return True
        return False

    def get_distance(self, atom1, atom2, limit=None, wrap_self=True):
        """
        Calculate the shortest distance between two atoms.

        .. Note::
            This is not as trivial a problem as it sounds. It is easy to
            demonstrate that for any non-cubic cell, the normal method of
            calculating the distance by wrapping the vector in fractional
            coordinates to the range (-0.5, 0.5) fails for cases near (0.5,0.5)
            in Type I cells and near (0.5, -0.5) for Type II.

            To get the correct distance, the vector must be wrapped into the
            Wigner-Seitz cell.

        Arguments:
            atom1, atom2: (:mod:`~simulation.Atom`, :mod:`~simulation.Site`, int).

        Keyword Arguments:
            limit:
                If a limit is provided, returns None if the distance is
                greater than the limit.

            wrap_self:
                If True, the distance from an atom to itself is 0, otherwise it
                is the distance to the shortest periodic image of itself.

        """
        if isinstance(atom1, int):
            a1 = self.atoms[atom1].coord
        elif isinstance(atom1, (Atom, Site)):
            a1 = atom1.coord
        if isinstance(atom2, int):
            a2 = self.atoms[atom2].coord
        elif isinstance(atom2, (Atom, Site)):
            a2 = atom2.coord

        x, y, z = self.cell
        xx = self.metrical_matrix[0, 0]
        yy = self.metrical_matrix[1, 1]
        zz = self.metrical_matrix[2, 2]

        vec = a2 - a1
        vec -= np.round(vec)
        dist = np.dot(vec, self.cell)

        dist -= np.round(dist.dot(x) / xx) * x
        dist -= np.round(dist.dot(y) / yy) * y
        dist -= np.round(dist.dot(z) / zz) * z

        if limit:
            if any([abs(d) > limit for d in dist]):
                return None

        dist = la.norm(dist)
        if not wrap_self:
            if abs(dist) < 1e-4:
                dist = min(self.lp[:3])

        if limit:
            if dist > limit:
                return None

        return dist

    def _get_vector(self, atom1, atom2):
        x, y, z = self.cell
        xx = self.metrical_matrix[0, 0]
        yy = self.metrical_matrix[1, 1]
        zz = self.metrical_matrix[2, 2]

        vec = atom2.coord - atom1.coord
        vec -= np.round(vec)
        dist = np.dot(vec, self.cell)

        dist -= round(dist.dot(x) / xx) * x
        dist -= round(dist.dot(y) / yy) * y
        dist -= round(dist.dot(z) / zz) * z
        return dist

    def add_site(self, site):
        site.structure = self
        self.sites.append(site)
        for a in site.atoms:
            a.structure = self
            self.atoms.append(a)
        self.spacegroup = None

    def atom_on_site(self, atom, site, tol=1e-2):
        if abs(shortest_dist(atom, self.cell) - shortest_dist(site, self.cell)) < tol:
            _dist = self.get_distance(atom, site, limit=tol, wrap_self=True)
            if _dist is None:
                return False
        else:
            return False
        return _dist < tol

    def add_atom(self, atom, tol=0.01):
        """
        Adds `atom` to the structure if it isn't already contained.
        """
        if not self.atoms or not self.sites:
            atom.structure = self
            self._atoms = [atom]
            site = atom.get_site()
            self._sites = [site]
            return
        elif self.contains(atom, tol=tol):
            return
        self._atoms.append(atom)
        atom.structure = self
        for site in self.sites:
            if self.atom_on_site(atom, site, tol=tol):
                site.add_atom(atom, tol=tol)
                break
            else:
                site = atom.get_site()
                if not site in self._sites:
                    self._sites.append(site)
        self.spacegroup = None

    def sort(self):
        self.atoms = sorted(self.atoms)

    def set_composition(self, value=None):
        if value is None:
            self.composition = Composition.get(self.comp)
        return self.composition


    @property
    def comp(self):
        """Composition dictionary."""
        comp = {}
        for atom in self.atoms:
            elt = atom.element_id
            comp[elt] = comp.get(elt, 0) + atom.occupancy
        return comp

    @property
    def spec_comp(self):
        """Species composition dictionary."""
        spec_comp = {}
        for atom in self.atoms:
            spec = atom.species
            spec_comp[spec] = spec_comp.get(spec, 0) + atom.occupancy
        return spec_comp

    @property
    def name(self):
        """Unformatted name."""
        return format_comp(self.comp)

    @property
    def coords(self):
        """numpy.ndarray of atom coordinates."""
        return np.array([atom.coord for atom in self.atoms])

    @property
    def site_coords(self):
        """numpy.ndarray of site coordinates."""
        return np.array([site.coord for site in self.sites])

    @site_coords.setter
    def site_coords(self, coords):
        assert len(self.sites) == len(coords)
        for site, coord in zip(self.sites, coords):
            site.coord = wrap(coord)
            site._dist = None

    @property
    def site_types(self):
        return sorted(set([format_comp(s.comp) for s in self.sites]))

    @coords.setter
    def coords(self, coords):
        if len(coords) != len(self.atoms):
            raise ValueError('%s != %s' % (len(coords), len(self)))
        for a, c in zip(self.atoms, coords):
            c = np.array(map(float, c))
            a.coord = wrap(c)
            a._dist = None

    @property
    def magmoms(self):
        """numpy.ndarray of magnetic moments of shape (natoms,)."""
        return np.array([atom.magmom for atom in self.atoms])

    @magmoms.setter
    def magmoms(self, moms):
        for mom, atom in zip(self, moms):
            atom.magmom = mom

    @property
    def cartesian_coords(self):
        """Return atomic positions in cartesian coordinates."""
        return np.array([atom.cart_coord for atom in self.atoms])

    @cartesian_coords.setter
    def cartesian_coords(self, cc):
        for atom, coord in zip(self.atoms, cc):
            atom.cart_coord = coord

    @property
    def forces(self):
        """numpy.ndarray of forces on atoms."""
        forces = []
        for atom in self.atoms:
            forces.append(atom.forces)
        return np.array(forces)

    @forces.setter
    def forces(self, forces):
        for forces, atom in zip(forces, self.atoms):
            atom.forces = force

    @property
    def reciprocal_lattice(self):
        """Reciprocal lattice of the structure."""
        if self._reciprocal_lattice is None:
            self._reciprocal_lattice = la.inv(self.cell).T
        return self._reciprocal_lattice

    _inv = None

    @property
    def inv(self):
        """
        Precalculates the inverse of the lattice, for faster conversion
        between cartesian and direct coordinates.
        """
        if self._inv is None:
            self._inv = la.inv(self.cell)
        return self._inv


    @property
    def similar(self):
        return Structure.objects.filter(natoms=self.natoms,
                                        composition=self.composition,
                                        spacegroup=self.spacegroup,
                                        label=self.label).exclude(id=self.id)

    def set_natoms(self, n):
        """Set self.atoms to n blank Atoms."""
        self.atoms = [Atom() for i in range(n)]
        self._sites = None

    def set_nsites(self, n):
        """Sets self.sites to n blank Sites."""
        self.sites = [Site() for i in range(n)]
        self._atoms = None


    def make_primitive(self, in_place=True, tol=1e-3):
        """Uses spglib to convert to the primitive cell.

        Keyword Arguments:
            in_place:
                If True, changes the current structure. If false returns
                a new one

            tol:
                Symmetry precision for symmetry analysis

        Examples::

            >>> s = io.read(INSTALL_PATH+'io/files/POSCAR_FCC')
            >>> print len(s)
            4
            >>> s.make_primitive()
            >>> print len(s)
            1

        """
        if not in_place:
            new = self.copy()
            new.make_primitive(tol=tol)
            return new

        find_primitive(self, symprec=tol)

    def get_sites(self, tol=0.1):
        """
        From self.atoms, creates a list of Sites. Atoms which are closer
        than tol from one another are considered on the same site.

        """
        if not any([a.occupancy < 1 for a in self.atoms]):
            self._sites = [a.get_site() for a in self.atoms]
            return self._sites

        _sites = []
        for atom in self.atoms:
            site = atom.get_site()
            site.structure = self
            if not any([site is site2 for site2 in _sites]):
                _sites.append(site)
        self._sites = _sites
        return self._sites

    def group_atoms_by_symmetry(self):
        """Sort self.atoms according to the site they occupy."""
        eq = get_symmetry_dataset(self)['equivalent_atoms']
        resort = np.argsort(eq)
        self._atoms = list(np.array(self._atoms)[resort])



    @property
    def is_perfect(self):
        if any([s.partial for s in self.sites]):
            return False
        return True
