from rest_framework import viewsets
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
from .serializers import*
from simulation.materials.element import Element, Species
from simulation.materials.entry import Entry
from simulation.materials.composition import Composition
from simulation.materials.structure import Structure
from simulation.materials.atom import Atom, Site
from simulation.analysis.vasp.calculation import Calculation
from simulation.analysis.vasp.dos import DOS
from simulation.analysis.symmetry.spacegroup import Spacegroup, WyckoffSite

import datetime


class SpacegroupViewSet(viewsets.ModelViewSet):
    queryset = Spacegroup.objects.all().order_by('number')
    serializer_class = SpacegroupSerializer


class WyckoffSiteViewSet(viewsets.ModelViewSet):
    queryset = WyckoffSite.objects.all().order_by('id')
    serializer_class = WyckoffSiteSerializer


class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all().order_by('name')
    serializer_class = ElementSerializer

class SpeciesViewSet(viewsets.ModelViewSet):
    queryset = Species.objects.all().order_by('name')
    serializer_class = SpeciesSerializer

class CalculationViewSet(viewsets.ModelViewSet):
    queryset = Calculation.objects.all().order_by('id')
    serializer_class = CalculationSerializer


class DosViewSet(viewsets.ModelViewSet):
    queryset = DOS.objects.all().order_by('id')
    serializer_class = DosSerializer

class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all().order_by('id')
    serializer_class = EntrySerializer


class CompositionViewSet(viewsets.ModelViewSet):
    queryset = Composition.objects.all().order_by('id')
    serializer_class = CompositionSerializer



class StructureViewSet(viewsets.ModelViewSet):
    queryset = Structure.objects.all().order_by('id')
    serializer_class = StructureSerializer


class AtomViewSet(viewsets.ModelViewSet):
    queryset = Atom.objects.all().order_by('id')
    serializer_class = AtomSerializer



class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all().order_by('id')
    serializer_class = AtomSerializer



