from django_filters.rest_framework import filters
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from simulation.analysis.vasp.calculation import Calculation

class CalculationFilter(django_filters.FilterSet):
    band_gap = filters.RangeFilter()
    formation_energy = filters.RangeFilter()
    spacegroup_number = django_filters.NumberFilter(field_name='output__spacegroup__number', lookup_expr='exact')
    lattice_system = django_filters.CharFilter(field_name='output__spacegroup__lattice_system', lookup_expr='icontains')
    
    class Meta:
        model = Calculation
        fields = [
            'band_gap',
            'formation_energy',
            'spacegroup_number',
            'lattice_system',
        ]
