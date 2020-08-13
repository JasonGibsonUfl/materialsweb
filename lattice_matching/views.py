from django.shortcuts import render
from lattice_matching.eg_Ima import  StructureMatcher
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen import Structure

from django.core.files.storage import FileSystemStorage
# Create your views here.
def lattice_matching_view(request, *args,**kwargs):
    context = {}
    is_signed_in = request.user.is_authenticated and not request.user.is_anonymous
    context.update({"is_signed_in": is_signed_in})

    if request.method == 'POST':
        user_input_1 = request.FILES.get('user_input_1', None)
        user_input_2 = request.FILES.get('user_input_2', None)
        user_input_1 = user_input_1.read().decode("utf-8")
        user_input_2 = user_input_2.read().decode("utf-8")
        user_area = request.POST.get('user_area', None)
        user_strain = request.POST.get('user_strain', None)
        a= StructureMatcher(user_input_1, user_input_2, float(user_area), float(user_strain))
        context.update({"data": a})
        context.update({"structure_1": get_jmol3(user_input_1)})



    return render(request, 'lattice.html', context)

def get_jmol3(structure):
    structure = Structure.from_str(structure, fmt='poscar')
    analyzer = SpacegroupAnalyzer(structure)
    structure = analyzer.get_refined_structure()
    structure.make_supercell([2, 2, 2])
    xyz_structure = [str(structure.num_sites),structure.composition.reduced_formula]
    for site in structure.sites:
        element = site._species.reduced_formula.replace('2', '')
        atom = '{} {} {} {}'.format(element, str(site.x), str(site.y),str(site.z))
        xyz_structure.append(atom)
    string = str(xyz_structure)
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace(', ', r'\n')
    string = string.replace("'", "")
    return string