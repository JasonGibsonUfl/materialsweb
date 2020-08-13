# coding: utf-8
# Copywrite (c) Henniggroup.
# Distributed under the terms of the MIT License.

from __future__ import division, unicode_literals, print_function

"""
Utility script to find if endpoint slabs are matching with substrate

Usage: Provide inputs <path to poscar substrate>, <path to poscar 2D> and
       match constraints using for the search

       python get_matching_matrix.py
"""
# import the lma module
# from mpinterfaces import transformations
from . import transformations
from pymatgen import Structure, Lattice
import numpy as np
import os


#### Inputs for lattice matching #####
# substrate file path

# After this point, I started messing with Chaitanya's stuff, I also muted all print statements
# from his transformations.py file. Gotta be honest, I'm not the best coder, hopefully this works
# - Devin
def StructureMatcher(user_input_one, user_input_two, user_area, user_strain,
                     all_matches=True):
    # Output message is only used if the algorithm fails or if the user did not enter POSCAR files
    output_message = ""
    associated_areas = []
    associated_ustrains = []
    associated_vstrains = []
    sub = None
    twod = None
    # user_input_one is a POSCAR file or string of a POSCAR file
    # User_input_two is another POSCAR file or string of a POSCAR file
    # user_area is the maximum area of the combined heterostructure in squared Angstroms
    # user_strain is the maximum strain in decimal form (i.e. 0.06 would be 6% strain)
    # all_matches specifies whether the code should spit out all possible matches
    sub = Structure.from_str(user_input_one,fmt='poscar')
    try:
        sub = Structure.from_str(user_input_one, fmt='poscar')
        twod = Structure.from_str(user_input_two, fmt='poscar')
    except:
        output_message = "These are not recognizable POSCARs, try again."
        print(output_message)

    # provide input match constraints as a dictionary
    match_constraints = {'max_area': user_area, 'max_mismatch': user_strain, 'max_angle_diff': 4,
                         'r1r2_tol': 0.04, 'separation': 2.2, 'nlayers_substrate': 1,
                         'nlayers_2d': 1, 'sd_layers': 0, 'best_match': 'area'}

    structs = []

    if all_matches:
        all_ifaces, all_n_subs, all_z_ubs, uv_all = transformations.run_lat_match(sub, twod,
                                                                                  match_constraints, all_matches=True)

        all_ifaces = [i for i in all_ifaces if i is not None]
        all_n_subs = [i for i in all_n_subs if i is not None]
        all_z_ubs = [i for i in all_z_ubs if i is not None]

        # NOTE: use z_ub to put sd flags on the fly
        count = 0
        for i, iface in enumerate(all_ifaces):
            strct = Structure(iface.lattice, iface.species, iface.frac_coords)
            structs.append(strct)
            associated_areas.append(uv_all[count][2])
            associated_ustrains.append(uv_all[count][3] * 100)
            associated_vstrains.append(uv_all[count][4] * 100)
            count += 1;
    else:
        # Lowest area (default) or minimum uv mismatched lattice match
        # is returned based on 'best_match' option in match_constraints
        # best_match should be either 'area' or 'mismatch'
        iface, n_sub, z_ub = transformations.run_lat_match(sub, twod, match_constraints)

        if iface is None:
            # print ('Try changing the parameters.')
            output_message = "No structures found, try changing parameters"
        else:
            strct = Structure(iface.lattice, iface.species, iface.frac_coords)
            structs.append(strct)
    return output_message, structs, associated_ustrains, associated_vstrains, associated_areas