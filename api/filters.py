from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from simulation.analysis.vasp.calculation import Calculation
class DynamicSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        return request.GET.getlist('search_fields', [])

class CalculationFilter(DjangoFilterBackend,):
    bandgap = filters.RangeFilter(name='bandgap')

    class Meta:
        model = Calculation
