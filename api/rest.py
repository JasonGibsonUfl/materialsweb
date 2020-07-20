import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "materialsweb2.settings")

django.setup()
import pymysql as dba
from simulation.materials.entry import Entry
from simulation.analysis.vasp.calculation import Calculation
from django.db.models import Q
import urllib
from ase.io import vasp
from dscribe.descriptors import SOAP

global url
url = 'http://10.5.46.39/static/'

class QueryEngine():

    # TODO: change to read only .cnf file
    #db = dba.connect(read_default_file='/etc/mysql/my.cnf')
    #cursor = db.cursor()

    def get_calculation(self, band_gap_range=None, formation_energy_range=None, elements=[], space_group_number=None,
                        dimension=None, crystal_system= None, name=None):
        print('query info    '+ ' band_gap_range: '+str(band_gap_range),' formation_energy_range: '+str(formation_energy_range)+' elements: '+str(elements)+' space_group_number: '+str(space_group_number)+' dimension: '+str(dimension)+' crystal_system: '+str(crystal_system))
        # TODO: Throw error for more than 2 inputs
        #all_results = Entry.objects.filter(calculation__band_gap__range=band_gap_range,
        #                                   calculation__formation_energy__range=formation_energy_range)
        all_results = []
        if len(elements) >0:
            print('in Elements')
            all_results = Calculation.objects.filter(element_set=elements.pop(0))
            for e in elements:
                all_results = all_results.filter(element_set=e)


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

        if len(all_results) == 0 :
            print('NO Results')
            all_results = Calculation.objects.all()

        all_results = all_results.distinct()
        if name != None:
            for a in all_results:
                if a.entry.name == name:
                    return [a]
        return all_results

    def element_query(self, elements=[],Ql=[]):
        if len(elements) > 0:
            Ql.append(Q(element_set=elements.pop(0)))
            print('here')
            QueryEngine.element_query(self, elements=elements, Ql=Ql)
        return Ql

    def element_query_set(self, elements):
        element_query2=QueryEngine.element_query(self, elements=elements)
        for el in element_query2:
            try:
                query_set = query_set.filter(el)
            except:
                query_set = Calculation.objects.filter(el)
        return query_set

    @staticmethod
    def get_KRR(system):
        '''
        Method to allow easy access to all pre-trainned kernal ridge regresion machine learning models of GASP runs
        Args:
            system (str): A chemical system (e.g. Cd-Te)
        returns:
            pickle object of machine learning model
        '''
        import pickle
        urlm =url+'models/'+system+'.sav'
        print(urlm)
        model = pickle.load(urllib.request.urlopen(urlm))
        return model

    '''Machine Learning'''
    @staticmethod
    def get_soap(file, rcut=7, nmax=5, lmax=8):
        print('./' + file)
        ml=vasp.read_vasp('./'+file)
        species=['Cd','Te']
        periodic_soap = SOAP(
        periodic=True,
        species=species,
        rcut=rcut,
        nmax=nmax,
        lmax=lmax,
        rbf='gto',
        sigma=0.125,
        average=True
        )
        soap = periodic_soap.create(ml)
        #soap = 1
        return soap