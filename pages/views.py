from django.shortcuts import render
from simulation.materials.entry import Entry
from simulation.analysis.vasp.calculation import Calculation
from simulation.materials.structure import Structure
from api.rest import QueryEngine
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
        
        if all(v == 0 for v in dimensions):
            dimensions = None
        print(dimensions)
        qe = QueryEngine()
        all_results = qe.get_calculation(elements=formula, band_gap_range=band_range, formation_energy_range=formation_energy_range ,dimension=dimensions)

        context = {
            'all_results': all_results
        }
        print(len(context['all_results']))
        #context = 'TEMP'
    else:
        split_formula = ''
        context = {'redform': '', 'alp': '', 'clp': '',
                   'structure': CAFFEINE,
                   'evpa': '', 'ion_conc': '-6', 'all_results': ''}
    #is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    #context.update({"is_signed_in": is_signed_in})
    #print("HERE"+str(len(formula.split('-'))))

    return render(request, 'database.html', context)


def result_view(request, *args, **kwargs):
    full_path = request.get_full_path()
    mwid = full_path.split('/')[-1]
    entry = Entry.objects.get(id=mwid)
    path = entry.path
    calculation = Calculation.objects.get(path=path)
    band_gap = round(calculation.dos.find_gap(),3)
    ##TEST
    if band_gap != 0:
        if(calculation.is_direct):
            direct = 'direct'
        else:
            direct = 'indirect'
    else:
        direct = ''
    path = str(path.split('/')[-1])
    label = path
    formation_energy = calculation.formation_energy
    structure = Structure.objects.get(label=path)
    a = [abs(structure.x1), abs(structure.x2), abs(structure.x3)]
    a = max(a)
    b = max([abs(structure.y1), abs(structure.y2), abs(structure.y3)])

    print(calculation)
    context = {
        'entry': entry,
        'path': path,
        'a': a,
        'b': b,
        'structure': structure,
        'data': structure.get_jmol(),
        'label': label,
        'formation_energy': formation_energy,
        'band_gap': band_gap,
        'direct': direct,

    }

    return render(request, 'result.html', context)


