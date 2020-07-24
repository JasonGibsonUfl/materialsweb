from django_filters.rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from simulation.analysis.vasp.calculation import Calculation

class CalculationFilter(DjangoFilterBackend,):
    bandgap = filters.RangeFilter(name='bandgap')

    class Meta:
        model = Calculation
