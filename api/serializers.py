from rest_framework import serializers
from simulation.materials.element import Element, Species
from simulation.materials.entry import Entry
from simulation.materials.composition import Composition
from simulation.materials.structure import Structure
from simulation.materials.atom import Atom, Site
from simulation.analysis.vasp.calculation import Calculation
from simulation.analysis.vasp.dos import DOS
from simulation.analysis.symmetry.spacegroup import Spacegroup, WyckoffSite


class SpacegroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Spacegroup
        fields = '__all__'

class WyckoffSiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WyckoffSite
        fields = '__all__'


class ElementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Element
        fields = '__all__'

class SpeciesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Species
        fields = '__all__'



class CalculationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Calculation
        fields = '__all__'


class DosSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DOS
        fields = '__all__'

class EntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Entry
        fields = '__all__'


class CompositionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composition
        fields = '__all__'


class StructureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Structure
        fields = '__all__'


class AtomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Atom
        fields = '__all__'


class SiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'




