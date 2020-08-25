
# as above
import dash
import dash_html_components as html
import dash_core_components as dcc
import crystal_toolkit.components as ctc
from materialsweb2.settings import BASE_DIR
from lattice_matching.eg_Ima import  StructureMatcher

# standard Dash imports for callbacks (interactivity)
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import os
from pymatgen import Structure, Lattice
import base64
import xml.etree.ElementTree as et  
BASE_DIR = '/home/jason/temp'
UPLOAD_DIRECTORY = BASE_DIR+"/materialsweb/static/temp"

app = dash.Dash()

# now we give a list of structures to pick from
structures = [
    Structure(Lattice.cubic(4), ["Na", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]]),
    Structure(Lattice.cubic(5), ["K", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]]),
]

# we show the first structure by default
structure_component = ctc.StructureMoleculeComponent()#structures[0])
print(structure_component.id)
# and we create a button for user interaction
my_button = html.Button("Swap Structure", id="change_structure_button")

# now we have two entries in our app layout,
# the structure component's layout and the button
my_layout = html.Div([
    html.Div([
        dcc.Upload(
                children=html.Div(["click to upload POSCAR 1"]),
                id="upload_poscar_1",
                # id='vasprun_dos',

                style={'display': 'block',
                       'height': '30px',
                       'width': '100%',
                       'marginBottom': '5px',
                       'borderWidth': '1px',
                       'textAlign': 'center'
                       }
            ),
        dcc.Store(id='poscar_1'),

        html.Div([
            dcc.Upload(
                children=html.Div(["click to upload POSCAR 2"]),
                id="upload_pocar_2",
                # id='vasprun_dos',

                style={'display': 'block',
                       'height': '30px',
                       'width': '100%',
                       'marginBottom': '5px',
                       'borderWidth': '1px',
                       'textAlign': 'center'
                       }
            ),
            dcc.Store(id='poscar_2'),

            # html.H2("File List"),
        ]),
        html.Div([html.Div(id='output_structure'),])# my_button, structure_component.options_layout(),]),
        ])
    ])

ctc.register_crystal_toolkit(app=app, layout=my_layout, cache=None)

# for the interactivity, we use a standard Dash callback
@app.callback(
    Output(structure_component.id(), "data"),
    [Input("change_structure_button", "n_clicks")],
)
def update_structure(n_clicks):
    # on load, n_clicks will be None, and no update is required
    # after clicking on the button, n_clicks will be an int and incremented
    if not n_clicks:
        raise PreventUpdate
    return structures[n_clicks % 2]


@app.callback(
    Output('upload_structures','component'),
    [Input('poscar_1','value'),Input('poscar_2','value')]
)
def upload_structure(poscar_1, poscar_2):
    a = StructureMatcher(poscar_1, poscar_2, float(20), float(5))
    return ctc.StructureMoleculeComponent(a[1][0])

@app.callback(
    Output('poscar_1', 'value'),  # "file-list"),#, "children"),
    [Input("upload_poscar_1", "filename"), Input("upload_poscar_1", "contents")]#, Input("upload_poscar_2", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        # for name, data in zip(uploaded_filenames, uploaded_file_contents):
        print(uploaded_filenames)
        save_file(str(uploaded_filenames), uploaded_file_contents)

        return UPLOAD_DIRECTORY + '/' + str(uploaded_filenames)

@app.callback(
    Output('poscar_2', 'value'),  # "file-list"),#, "children"),
    [Input("upload_poscar_2", "filename"), Input("upload_poscar_2", "contents")]
    # , Input("upload_poscar_2", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        # for name, data in zip(uploaded_filenames, uploaded_file_contents):
        print(uploaded_filenames)
        save_file(str(uploaded_filenames), uploaded_file_contents)

        return UPLOAD_DIRECTORY + '/' + str(uploaded_filenames)
    '''#
    data = poscar_1.encode("utf8").split(b";base64,")[1]
    string1 = (str(base64.decodebytes(data),'utf-8'))    
    #struc1=Structure.from_str(string,fmt='poscar')
    data = poscar_2.encode("utf8").split(b";base64,")[1]
    string2 = (str(base64.decodebytes(data),'utf-8'))
    a = StructureMatcher(string1, string2, float(20), float(5))
    print(a[1][0])
    structure_component = ctc.StructureMoleculeComponent(a[1][0])
    children = html.Div([structure_component, structure_component.options_layout(),])
    return children
    #children = ctc.StructureMoleculeComponent(a[1][0])
    #return children
    '''

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


# as above
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)