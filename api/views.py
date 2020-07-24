from rest_framework import viewsets, filters
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
    http_method_names = ['get']

class WyckoffSiteViewSet(viewsets.ModelViewSet):
    queryset = WyckoffSite.objects.all().order_by('id')
    serializer_class = WyckoffSiteSerializer
    http_method_names = ['get']

class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all().order_by('name')
    serializer_class = ElementSerializer
    http_method_names = ['get']

class SpeciesViewSet(viewsets.ModelViewSet):
    queryset = Species.objects.all().order_by('name')
    serializer_class = SpeciesSerializer
    http_method_names = ['get']

from api.filters import DynamicSearchFilter
from django_filter.rest_framework import DjangoFilterBackend
class CalculationViewSet(viewsets.ModelViewSet):
    queryset = Calculation.objects.all().order_by('id')
    serializer_class = CalculationSerializer
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend,)

    filter_fields = ['dimension','natoms']

class DosViewSet(viewsets.ModelViewSet):
    queryset = DOS.objects.all().order_by('id')
    serializer_class = DosSerializer
    http_method_names = ['get']

class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all().order_by('id')
    serializer_class = EntrySerializer
    http_method_names = ['get']


class CompositionViewSet(viewsets.ModelViewSet):
    queryset = Composition.objects.all().order_by('id')
    serializer_class = CompositionSerializer
    http_method_names = ['get']

class StructureViewSet(viewsets.ModelViewSet):
    queryset = Structure.objects.all().order_by('id')
    serializer_class = StructureSerializer
    http_method_names = ['get']

class AtomViewSet(viewsets.ModelViewSet):
    queryset = Atom.objects.all().order_by('id')
    serializer_class = AtomSerializer
    http_method_names = ['get']

class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all().order_by('id')
    serializer_class = AtomSerializer
    http_method_names = ['get']
