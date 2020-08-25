# standard Dash imports
import dash
import dash_html_components as html
import dash_core_components as dcc
from lattice_matching.eg_Ima import  StructureMatcher

# standard Crystal Toolkit import
import crystal_toolkit.components as ctc

# import for this example
from pymatgen import Structure, Lattice

# create Dash app as normal
app = dash.Dash()

# create the Structure object
structure1 = Structure.from_file('/home/jason/Downloads/POSCAR')

# create the Crystal Toolkit component
user_input_1 = '/home/jason/Downloads/POSCAR_sub'
user_input_2 = '/home/jason/Downloads/POSCAR_twod'

structure2 = Structure.from_file(user_input_1)
structure3 = Structure.from_file(user_input_2)

struct_list= StructureMatcher(user_input_1, user_input_2, float(20), float(5))
structures=[structure1, structure2, structure3]
struct_list.append(structures)
structure = struct_list[1][0]
structure_component = ctc.StructureMoleculeComponent(structure, id="my_structure")

# example layout to demonstrate capabilities of component
my_layout = html.Div(
    [
    html.Div(
        [
            html.H3('POSCAR 1', ),

            dcc.Upload(
                children=html.Div(["POSCAR 1"]),
                id="poscar_1",
            ),

            html.H3('POSCAR 2'),

            dcc.Upload(
                children=html.Div(["POSCAR 2"]),
                id="poscar_2",
            ),

            html.H3('Area (Angstrom^2)'),

            dcc.Input(
                type ="text",
                name="user_area",
                value="20",
                id="user_area"
            ),

            html.H3('Strain (%)'),

            dcc.Input(
                type="text",
                name="user_strain",
                value="5",
                id="user_strain"
            ),

        ],
        #style={'display' : 'table-column'},
        style={'float': 'left', 'width': '33%'},

        #style={'width': '33%', 'display': 'inline-block', 'position' : 'relative'}
    ),
    html.Div(
        [
            structure_component.title_layout(),
            structure_component.layout(size="400px"),
            structure_component.legend_layout(),
        ],
        style={'float': 'left', 'width': '33%'},

        #style={'width': '33%', 'display': 'inline-block', 'position' : 'relative'}
    ),
    html.Div(
        [
            html.H2("Optional Additional Layouts"),
            html.H3("Screenshot Layout"),
            structure_component.screenshot_layout(),
            html.H3("Options Layout"),
            structure_component.options_layout(),
        ],
        #style={'display': 'table-column'},
        style={'float': 'left', 'width': '33%'},
        #style={'width': '33%', 'display': 'inline-block', 'position' : 'relative'}
    ),

    ]
)

# tell crystal toolkit about your app and layout
ctc.register_crystal_toolkit(app, layout=my_layout)

# allow app to be run using "python structure.py"
# in production, deploy behind gunicorn or similar
# see Dash documentation for more information
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
