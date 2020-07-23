from rest_framework import serializers
from simulation.materials.element import Element
from simulation.analysis.vasp.calculation import Calculation


class ElementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Element
        fields = '__all__'

from rest_framework import serializers
from simulation.materials.element import Element


class CalculationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Calculation
        fields = '__all__'
