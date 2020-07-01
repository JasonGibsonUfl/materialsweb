import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "materialsweb2.settings")

django.setup()
import pymysql as dba
from simulation.materials.entry import Entry
from simulation.analysis.vasp.calculation import Calculation
from django.db.models import Q

class QueryEngine():

    # TODO: change to read only .cnf file
    #db = dba.connect(read_default_file='/etc/mysql/my.cnf')
    #cursor = db.cursor()

    def get_calculation(self, band_gap_range=None, formation_energy_range=None, elements=None, space_group_number=None,
                        dimension=None, crystal_system= None):
        print('self' + self)
        print('query info    '+ ' band_gap_range: '+str(band_gap_range),' formation_energy_range: '+str(formation_energy_range)+' elements: '+str(elements)+' space_group_number: '+str(space_group_number)+' dimension: '+str(dimension)+' crystal_system: '+str(crystal_system))
        # TODO: Throw error for more than 2 inputs
        #all_results = Entry.objects.filter(calculation__band_gap__range=band_gap_range,
        #                                   calculation__formation_energy__range=formation_energy_range)
        all_results = []
        print('len all '+str(len(all_results)))
        if elements != None:
            print("ELEMENTS")
            all_results = QueryEngine.element_query_set(self,elements)

        if band_gap_range != None:
            if len(all_results)>0:
                all_results = all_results.filter(band_gap__range=band_gap_range)
            else:
                all_results = Calculation.objects.filter(band_gap__range=band_gap_range)

        if formation_energy_range != None :
            if len(all_results) > 0:
                all_results = all_results.filter(formation_energy__range=formation_energy_range)
            else:
                all_results = Calculation.objects.filter(formation_energy__range=formation_energy_range)

        if(space_group_number != None):
            if len(all_results)>0:
                all_results = all_results.filter(entry__structure__spacegroup__number=space_group_number)
            else:
                all_results = Calculation.objects.filter(entry__structure__spacegroup__number=space_group_number)

        if (dimension != None):
            if len(all_results) > 0:
                all_results = all_results.filter(dimension__in=dimension)
            else:
                all_results = Calculation.objects.filter(dimension__in=dimension)

        if ( crystal_system!= None):
            if len(all_results) > 0:
                all_results = all_results.filter(entry__structure__spacegroup__lattice_system__in=crystal_system)
            else:
                all_results = Calculation.objects.filter(entry__structure__spacegroup__lattice_system__in=crystal_system)

        all_results = all_results.distinct()

        return all_results

    def element_query(self, elements=[],Ql=[]):
        if len(elements) > 0:
            Ql.append(Q(element_set=elements.pop(0)))
            print('here')
            QueryEngine.element_query(self, elements=elements, Ql=Ql)
        return Ql

    def element_query_set(self, elements):
        element_query=QueryEngine.element_query(self, elements=elements)
        for el in element_query:
            try:
                query_set = query_set.filter(el)
            except:
                query_set = Calculation.objects.filter(el)
        return query_set
