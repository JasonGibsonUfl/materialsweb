from django_filters.rest_framework import filters
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from simulation.analysis.vasp.calculation import Calculation

class CalculationFilter(django_filters.FilterSet):
    bandgap = filters.RangeFilter(name='bandgap')

    class Meta:
        model = Calculation
        fields = ['bandgap']
