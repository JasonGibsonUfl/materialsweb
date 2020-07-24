from django_filters.rest_framework import filters
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from simulation.analysis.vasp.calculation import Calculation

class CalculationFilter(django_filters.FilterSet):
    band_gap = filters.RangeFilter()

    class Meta:
        model = Calculation
        fields = ['band_gap','entry__structure__spacegroup__lattice_system']
