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
        print((a[1][-1]))
        s3 =a[1][-1].to(fmt='poscar')
        context.update({"data": a})
        context.update({"structure_1": get_jmol2(Structure.from_str(user_input_1, fmt='poscar'))})
        context.update({"structure_2": get_jmol2(Structure.from_str(user_input_2, fmt='poscar'))})
        context.update({"structure_3": get_jmol3(Structure.from_str(s3, fmt='poscar'))})


    return render(request, 'test.html', context)

def get_jmol3(structure):
    analyzer = SpacegroupAnalyzer(structure)
    structure = analyzer.get_refined_structure()
    structure.make_supercell([2, 2, 2])
    xyz_structure = [str(structure.num_sites),structure.composition.reduced_formula]
    for site in structure.sites:
        element = site._species.reduced_formula.replace('2', '')
        print(element)
        atom = '{} {} {} {}'.format(element, str(site.x), str(site.y),str(site.z))
        xyz_structure.append(atom)
    string = str(xyz_structure)
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace(', ', r'\n')
    string = string.replace("'", "")
    string = string.replace('Se', 'H')
    print(string)
    return string

def get_jmol2(structure):
    from pymatgen.core.operations import SymmOp
    needs_shift = False
    if structure.lattice.a == max(structure.lattice.abc):
        translation = SymmOp.from_rotation_and_translation(translation_vec=(structure.lattice.a / 2, 0, 0))
        for site in structure.sites:
            if site._frac_coords[0] > 0.9 or site._frac_coords[0] < 0.1:
                needs_shift = True
        if needs_shift:
            structure.apply_operation(translation)
        structure.make_supercell([1, 6, 6])
    elif structure.lattice.b == max(structure.lattice.abc):
        translation = SymmOp.from_rotation_and_translation(translation_vec=(0, structure.lattice.b / 2, 0))
        for site in structure.sites:
            if site._coords[1] > 0.9 or site._coords[1] < 0.1:
                needs_shift = True
        if needs_shift:
            structure.apply_operation(translation)
        structure.make_supercell([6, 1, 6])
    else:
        translation = SymmOp.from_rotation_and_translation(translation_vec=(0, 0, structure.lattice.c / 2))
        for site in structure.sites:
            if site._frac_coords[2] > 0.9 or site._frac_coords[2] < 0.1:
                needs_shift = True
        if needs_shift:
            structure.apply_operation(translation)

        structure.make_supercell([6, 6, 1])
        print('frac_coord: '+ str(site._frac_coords[2]))

    print(structure.lattice.b)
    xyz_structure = [str(structure.num_sites),structure.composition.reduced_formula]
    for site in structure.sites:
        element = site._species.reduced_formula.replace('2', '')
        atom = '{} {} {} {}'.format(element, str(site.x), str(site.y),str(site.z))
        xyz_structure.append(atom)
    #return '+'.join(xyz_structure)
    string = str(xyz_structure)
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace(', ', r'\n')
    string = string.replace("'", "")
    return string