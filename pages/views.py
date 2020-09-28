from django.shortcuts import render
from simulation.materials.entry import Entry
from simulation.analysis.vasp.calculation import Calculation
from simulation.materials.structure import Structure
from api.rest import QueryEngine
from pymatgen.core.structure import Structure as StructureP
from materialsweb2.settings import BASE_DIR
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
    return render(request, 'gasp.html', {})

def electronic_visualization_view(request, *args,**kwargs):
    return render(request, 'electronic_visualization.html', {})


def substrate_view(request, *args,**kwargs):
    return render(request, 'substrate.html', {})

def about_view(request, *args,**kwargs):
    context = {}
    is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    context.update({"is_signed_in": is_signed_in})
    return render(request, 'about.html', context)


def docs_view(request, *args,**kwargs):
    context = {}
    is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    context.update({"is_signed_in": is_signed_in})
    return render(request, 'docs.html', context)


def contact_view(request, *args,**kwargs):
    context = {}
    is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    context.update({"is_signed_in": is_signed_in})
    return render(request, 'contact.html', context)


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
        if '-' not in formula:
            name = formula
        else:
            name = None

        formula = str(formula).split('-')
        print(formula)
        if formula[-1] == '':
            print('in')
            formula = formula[0:-1]



        band_gap_min = request.POST.get('band_gap_min')
        band_gap_max = request.POST.get('band_gap_max')
        band_range = [band_gap_min, band_gap_max]
        formation_energy_min = request.POST.get('formation_energy_min')
        formation_energy_max = request.POST.get('formation_energy_max')
        if formation_energy_min == '-400.00' and formation_energy_max == '400.00':
            formation_energy_range=None
        else:
            formation_energy_range = [str(float(formation_energy_min)), str(float(formation_energy_max))]
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
        print(name)
        all_results = qe.get_calculation(elements=formula, band_gap_range=band_range,
                                         formation_energy_range=formation_energy_range,dimension=dimensions,
                                        crystal_system=select_crystal_systems, name=name)

        for a in all_results:
            if a.band_gap == None :
                a.band_gap = 'None'
            elif a.band_gap == 0.0:
                a.band_gap = '0.0000'
            else:
                a.band_gap = round(float(a.band_gap),4)


        context = {
            'all_results': all_results
        }

    else:
        context = { 'all_results': ''}


    return render(request, 'database.html', context)


def result_view(request, *args, **kwargs):
    full_path = request.get_full_path()
    print(full_path)
    mwid = full_path.split('/')[-1]
    entry = Entry.objects.get(id=mwid)
    path = entry.path
    print(BASE_DIR + path.split('/var/www/materialsweb')[-1] + '/POSCAR')
    structure = StructureP.from_file(BASE_DIR + path.split('/var/www/materialsweb')[-1] + '/POSCAR')
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
    path = str(path.split('database/')[-1])
    label = path
    formation_energy = calculation.formation_energy
    a = round(structure.lattice.a, 3)
    b = round(structure.lattice.b, 3)
    structure = calculation.entry.structure
    formula = structure.composition.name

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
        'formula': formula,

    }

    return render(request, 'result.html', context)

from django.shortcuts import render
from lattice_matching.eg_Ima import  StructureMatcher
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen import Structure

from django.core.files.storage import FileSystemStorage
# Create your views here.
def models_view(request, *args,**kwargs):
    context = {}
    is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    context.update({"is_signed_in": is_signed_in})

    if request.method == 'POST':
        if 'submit' in request.POST:
            i = 0
            user_input_1 = request.FILES.get('user_input_1', None)
            user_input_2 = request.FILES.get('user_input_2', None)
            user_input_1 = user_input_1.read().decode("utf-8")
            user_input_2 = user_input_2.read().decode("utf-8")
            request.session['user_input_1'] = user_input_1
            request.session['user_input_2'] = user_input_2
            user_area = request.POST.get('user_area', None)
            user_strain = request.POST.get('user_strain', None)
            request.session['user_area'] = user_area
            request.session['user_strain'] = user_strain
            request.session['i'] = i
            a= StructureMatcher(user_input_1, user_input_2, float(user_area), float(user_strain))
            s3 =a[1][i].to(fmt='poscar')
            strain_u = a[2][i]
            strain_v = a[3][i]
            area = a[4][i]

        if 'next' in request.POST:
            print('NEXT!!!!!!!!!!!')
            user_input_1 = request.session.get('user_input_1')
            user_input_2 = request.session.get('user_input_2')
            user_area = request.session.get('user_area')
            user_strain = request.session.get('user_strain')
            i = request.session.get('i')
            i = i + 1
            a= StructureMatcher(user_input_1, user_input_2, float(user_area), float(user_strain))
            if i == len(a[1]):
                i = 0
            request.session['i'] = i
            print(i)
            s3 =a[1][i].to(fmt='poscar')
            strain_u = a[2][i]
            strain_v = a[3][i]
            area = a[4][i]

        context.update(({
            "data": a,

            "strain_u": strain_u,
            "strain_v": strain_v,
            "Area": area,
            "page_c": i+1,
            "page_t": len(a[1]),
            "download": s3,
        }))


    return render(request, 'models.html', context)
