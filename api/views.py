from rest_framework import viewsets
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
from .serializers import ElementSerializer, CalculationSerializer
from simulation.materials.element import Element
from simulation.analysis.vasp.calculation import Calculation

import datetime

class ElementViewSet(viewsets.ModelViewSet):
    queryset = Element.objects.all().order_by('name')
    serializer_class = ElementSerializer


class CalculationViewSet(viewsets.ModelViewSet):
    queryset = Calculation.objects.all().order_by('id')
    serializer_class = CalculationSerializer
