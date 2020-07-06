from django.shortcuts import render
from simulation.materials.entry import Entry
from simulation.analysis.vasp.calculation import Calculation
from simulation.materials.structure import Structure
from api.rest import QueryEngine
from pymatgen.core.structure import Structure as StructureP
from django.db.models import Q
import ast
import re
CAFFEINE = ('24+Caffeine+H -3.3804130 -1.1272367 0.5733036+N 0.9668296 '
            '-1.0737425 -0.8198227+C 0.0567293 0.8527195 0.3923156+N '
            '-1.3751742 -1.0212243 -0.0570552+C -1.2615018 0.2590713 '
            '0.5234135+C -0.3068337 -1.6836331 -0.7169344+C 1.1394235 '
            '0.1874122 -0.2700900+N 0.5602627 2.0839095 0.8251589+O '
            '-0.4926797 -2.8180554 -1.2094732+C -2.6328073 -1.7303959 '
            '-0.0060953+O -2.2301338 0.7988624 1.0899730+H 2.5496990 '
            '2.9734977 0.6229590+C 2.0527432 -1.7360887 -1.4931279+H '
            '-2.4807715 -2.7269528 0.4882631+H -3.0089039 -1.9025254 '
            '-1.0498023+H 2.9176101 -1.8481516 -0.7857866+H 2.3787863 '
            '-1.1211917 -2.3743655+H 1.7189877 -2.7489920 -1.8439205+C '
            '-0.1518450 3.0970046 1.5348347+C 1.8934096 2.1181245 '
            '0.4193193+N 2.2861252 0.9968439 -0.2440298+H -0.1687028 '
            '4.0436553 0.9301094+H 0.3535322 3.2979060 2.5177747+H '
            '-1.2074498 2.7537592 1.7203047')


# Create your views here.
def home_view(request, *args,**kwargs):
    is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    context= {"is_signed_in": is_signed_in}
    return render(request, 'home.html', context)

def gasp_view(request, *args,**kwargs):
    return render(request, 'test.html', {})

def substrate_view(request, *args,**kwargs):
    return render(request, 'substrate.html', {})

def about_view(request, *args,**kwargs):
    return render(request, 'about.html', {})


def docs_view(request, *args,**kwargs):
    return render(request, 'docs.html', {})


def contact_view(request, *args,**kwargs):
    return render(request, 'contact.html', {})


def api_view(request, *args,**kwargs):
    '''Note You must modify models in django to include an api key'''
    if request.user.is_authenticated and not request.user.is_anonymous:
        context = {"api_key": "Your API key is {}".format(
            request.user.api_key)}
    else:
        context = {
            "api_key": "Please sign in or register to obtain an API key."}
    is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    context.update({"is_signed_in": is_signed_in})
    return render(request, 'api2.html', context)


def database_view(request, *args,**kwargs):
   
    qe = QueryEngine()

    if request.POST.get('Submit'):
        context = {}
        dim1 = 0
        dim2 = dim1
        dim3 = dim2
        formula = request.POST.get('FormulaBox')
        formula = str(formula).split('-')
        print(formula)
        if formula[-1] == '':
            formula = formula[0:-1]
        else:
            formula = formula[-1]
            formula = re.sub(r'[0-9]+', '', formula)
            formula = re.findall('[A-Z][^A-Z]*', formula)
        print(formula)
        band_gap_min = request.POST.get('band_gap_min')
        band_gap_max = request.POST.get('band_gap_max')
        band_range = [band_gap_min, band_gap_max]
        
        formation_energy_min = request.POST.get('formation_energy_min')
        formation_energy_max = request.POST.get('formation_energy_max')
        if formation_energy_min == '-4.00' and formation_energy_max == '4.00':
            formation_energy_range=None
        else:
            formation_energy_range = [str(float(formation_energy_min)*1000.0), str(float(formation_energy_max)*1000.0)]
        if band_gap_min == '0.00' and band_gap_max == '10.00':
            band_range = None

        if str(request.POST.get('3D')) == 'on':
            dim3 = 3
        if str(request.POST.get('2D')) == 'on':
            dim2 = 2
        if str(request.POST.get('1D')) == 'on':
            dim1 = 1
        dimensions = [dim3, dim2, dim1]
        print(dimensions)
        if all(v == 0 for v in dimensions):
            dimensions = None
        select_crystal_systems=[]
        crystall_systems = ['hexagonal', 'monoclinic', 'orthorhombic', 'cubic', 'tetragonal', 'trigonal', 'triclinic']
        for system in crystall_systems:
            if str(request.POST.get(system)) == 'on':
                select_crystal_systems.append(system)
        if len(select_crystal_systems)==0:
            select_crystal_systems=None
        print(select_crystal_systems)
        all_results = []
        all_results = qe.get_calculation(elements=formula, band_gap_range=band_range,
                                         formation_energy_range=formation_energy_range,dimension=dimensions,
                                        crystal_system=select_crystal_systems, )
        for a in all_results:
            if a.band_gap == None :
                a.band_gap = 'None'
            elif a.band_gap == 0.0:
                a.band_gap = '0.0000'
            else:
                a.band_gap = round(float(a.band_gap),4)
            #if a.formation_energy == None :
                #a.formation_energy = 'None'
            #elif a.formation_energy == 0.0:
                #a.formation_energy = '0.0000'
            #else:
                #a.formation_energy = round(float(a.formation_energy),4)

        context = {
            'all_results': all_results
        }
        print(len(context['all_results']))
        #context = 'TEMP'
    else:
        context = { 'all_results': ''}


    return render(request, 'database.html', context)


def result_view(request, *args, **kwargs):
    full_path = request.get_full_path()
    print(full_path)
    mwid = full_path.split('/')[-1]
    entry = Entry.objects.get(id=mwid)
    path = entry.path
    structure = StructureP.from_file(path + '/POSCAR')
    calculation = Calculation.objects.get(path=path)
    band_gap = round(calculation.dos.find_gap(),3)
    ##TEST
    if band_gap != 0:
        print('bandGap  ' + str(calculation.is_direct))
        if(calculation.is_direct):
            direct = 'direct'
        else:
            direct = 'indirect'
    else:
        direct = ''
    path = str(path.split('/')[-1])
    label = path
    formation_energy = calculation.formation_energy
    a = structure.lattice.a
    b = structure.lattice.b
    structure = Structure.objects.get(label=path)
    print(calculation)
    if calculation.dimension == 2:
        print('Two Dimensional')
        data=structure.get_jmol2()
    else:
        print('Three Dimensional')
        data=structure.get_jmol3()
    context = {
        'entry': entry,
        'path': path,
        'a': a,
        'b': b,
        'structure': structure,
        'data': data,
        'label': label,
        'formation_energy': formation_energy,
        'band_gap': band_gap,
        'direct': direct,

    }

    return render(request, 'result.html', context)


