import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('SimpleExample', external_stylesheets=external_stylesheets)


app.layout = html.Div([

    html.H3('Interactive Electronic Structure Visualization Tool',
            style={'textAlign': 'center',
                   'color': '#0021A5'
                   }
            ),

    html.Div('currently a work in progress by Anne Marie Tan :)',
             style={'textAlign': 'center',
                    'color': '#FA4616',
                    'marginBottom': '20px'
                    }
             ),

    html.Div([

        ## hack whitespace between inline-blocks
        html.Div(style={'display': 'inline-block',
                        'width': '5%'
                        }
                 ),

        ## boxes to input path to local data
        html.Div([
            html.Div('From local data:',
                     style={'display': 'block'
                            }
                     ),

            dcc.Input(id='vasprun_dos',
                      type='text',
                      #                      value='',
                      placeholder='input path to vasprun.xml file from DoS calc. + enter/tab',
                      debounce=True,
                      style={'display': 'block',
                             'height': '30px',
                             'width': '100%',
                             'marginBottom': '5px',
                             'borderWidth': '1px',
                             'textAlign': 'center'
                             }
                      ),

            dcc.Input(id='vasprun_bands',
                      type='text',
                      #                      value='',
                      placeholder='input path to vasprun.xml file from bands calc. + enter/tab',
                      debounce=True,
                      style={'display': 'block',
                             'height': '30px',
                             'width': '100%',
                             'marginBottom': '5px',
                             'borderWidth': '1px',
                             'textAlign': 'center'
                             }
                      ),

            dcc.Input(id='kpts_bands',
                      type='text',
                      #                      value='',
                      placeholder='input path to KPOINTS file from bands calc. + enter/tab',
                      debounce=True,
                      style={'display': 'block',
                             'height': '30px',
                             'width': '100%',
                             'borderWidth': '1px',
                             'textAlign': 'center'
                             }
                      ),

            ## dcc.Store components are used to store JSON data in the browser
            ## (replace the "hidden Div" hack)
            dcc.Store(id='dos_object'),  ## pymatgen dos object
            dcc.Store(id='bs_object'),  ## pymatgen bs object
            dcc.Store(id='struct_object'),  ## pymatgen structure object
            dcc.Store(id='options'),  ## full dict of element/orbital options

        ],
            style={'display': 'inline-block',
                   'width': '30%',
                   'verticalAlign': 'top'
                   }
        ),

        ## hack whitespace between inline-blocks
        html.Div(style={'display': 'inline-block',
                        'width': '5%'
                        }
                 ),

        ## dropdown lists for selecting projections
        html.Div([
            html.Div('Select projections:',
                     style={'display': 'block'
                            }
                     ),

            dcc.Dropdown(
                id='species_dropdown',
                placeholder='select species',
                multi=True,
                style={'display': 'block',
                       'height': '34px',
                       'width': '100%',
                       'marginBottom': '5px',
                       'borderWidth': '1px'}
            ),

            dcc.Dropdown(
                id='orb_dropdown',
                placeholder='select orbital',
                multi=True,
                style={'display': 'block',
                       'height': '34px',
                       'width': '100%',
                       'marginBottom': '5px',
                       'borderWidth': '1px'}
            ),

            dcc.Dropdown(
                id='suborb_dropdown',
                placeholder='select sub-orbital',
                multi=True,
                style={'display': 'block',
                       'height': '34px',
                       'width': '100%',
                       'borderWidth': '1px'}
            ),

        ],
            style={'display': 'inline-block',
                   'width': '30%',
                   'verticalAlign': 'top'
                   }
        ),

        ## hack whitespace between inline-blocks
        html.Div(style={'display': 'inline-block',
                        'width': '5%'
                        }
                 ),

        ## button to click to generate bands+dos figure
        html.Button(id='submit_button',
                    n_clicks=0,
                    children='Generate plot',
                    style={'display': 'inline-block',
                           'height': '50px',
                           'width': '15%',
                           'verticalAlign': 'bottom'
                           }
                    ),
    ],
        style={'display': 'block',
               'marginBottom': '20px'
               }
    ),


    html.Div([
        ## our simple clickable structure figure!
        dcc.Graph(id='unitcell',
                  figure={'data': []},
                  style={'display': 'inline-block',
                         'width': '30%',
                         'height': '100%'
                         }
                  ),

        ## our interactive bands+dos figure!
        dcc.Graph(id='DOS_bands',
                  figure={'data': []},
                  style={'display': 'inline-block',
                         'width': '65%',
                         'height': '100%'
                         }
                  ),
    ],
        style={'display': 'block',
               'height': '600px'
               }
    ),

    ## this div tells which atom was selected (temporary)
    #    html.Div(id='select_atom',
    #            style={'display': 'inline-block',
    #                   'float': 'left',
    #                   'width': '30%',
    #                   'marginLeft': '100'
    #                   }
    #        ),

],
    style={'backgroundColor': '#FFFFFF'}
)


'''
app.layout = html.Div([
    html.H1('Square Root Slider Graph'),
    dcc.Graph(id='slider-graph', animate=True, style={"backgroundColor": "#1a2d46", 'color': '#ffffff'}),
    dcc.Slider(
        id='slider-updatemode',
        marks={i: '{}'.format(i) for i in range(20)},
        max=20,
        value=2,
        step=1,
        updatemode='drag',
    ),
])
'''
'''
@app.callback(
               Output('slider-graph', 'figure'),
              [Input('slider-updatemode', 'value')])
def display_value(value):


    x = []
    for i in range(value):
        x.append(i)

    y = []
    for i in range(value):
        y.append(i*i)

    graph = go.Scatter(
        x=x,
        y=y,
        name='Manipulate Graph'
    )
    layout = go.Layout(
        paper_bgcolor='#27293d',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[min(x), max(x)]),
        yaxis=dict(range=[min(y), max(y)]),
        font=dict(color='white'),

    )
    return {'data': [graph], 'layout': layout}
'''
from pymatgen.electronic_structure.dos import CompleteDos
from pymatgen.electronic_structure.bandstructure import BandStructureSymmLine
from .gen_bandsfig import BandsFig
from dash.dependencies import Input, Output, State
import json
import json
import numpy as np

from pymatgen import Structure
from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.electronic_structure.dos import CompleteDos
from pymatgen.electronic_structure.bandstructure import BandStructureSymmLine
from pymatgen.core.periodic_table import Element
# from pymatgen.ext.matproj import MPRester

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from .gen_structfig import StructFig
from .gen_bandsfig import BandsFig


@app.callback(Output('dos_object', 'data'),
              [Input('vasprun_dos', 'value')])
def get_dos(vasprun_dos):
    ## get CompleteDos object and "save" in hidden div in json format
    dos = Vasprun(vasprun_dos).complete_dos
    return json.dumps(dos.as_dict())



@app.callback(Output('bs_object', 'data'),
              [Input('dos_object', 'data'),
               Input('vasprun_bands', 'value'),
               Input('kpts_bands', 'value')])
def get_bs(dos, vasprun_bands, kpts_bands):
    ## get BandStructureSymmLine object and "save" in hidden div in json format
    bands = Vasprun(vasprun_bands, parse_projected_eigen=True)
    if dos:
        dos = CompleteDos.from_dict(json.loads(dos))
        bs = bands.get_band_structure(kpts_bands, line_mode=True, efermi=dos.efermi)
    else:
        bs = bands.get_band_structure(kpts_bands, line_mode=True)
    return json.dumps(bs.as_dict(), cls=MyEncoder)


@app.callback(Output('struct_object', 'data'),
              [Input('vasprun_dos', 'value'),
               Input('vasprun_bands', 'value')])
def get_structure(vasprun_dos, vasprun_bands):
    ## get structure object and "save" in hidden div in json format
    if vasprun_dos:
        structure = Vasprun(vasprun_dos).structures[-1]
    elif vasprun_bands:
        structure = Vasprun(vasprun_bands).structures[-1]
    return json.dumps(structure.as_dict())


@app.callback(Output('options', 'data'),
              [Input('struct_object', 'data')])
def get_options_all(struct):
    ## determine full list of options and store in hidden div

    ## de-serialize structure from json format to pymatgen object
    structure = Structure.from_dict(json.loads(struct))

    ## determine if sub-orbital projections exist. If so, set lm = True
    #    orbs = [Orbital.__str__(orb) for atom_dos in vasprun.complete_dos.pdos.values()
    #                                 for orb,pdos in atom_dos.items()]
    #    lm = any(["x" in s for s in orbs])

    ## determine the list of unique elements in the system
    elems = [str(site.specie) for site in structure.sites]
    ## remove duplicate entries
    options = dict.fromkeys(elems)

    ## generate the full list of options with sub-orbital projections
    for elem in options:
        options[elem] = {elem + ' Total': [elem + ' Total'],
                         elem + ' s': [elem + ' s']}
        if Element(elem).block == 'p' or Element(elem).block == 'd':
            options[elem].update({elem + ' p': [elem + ' px', elem + ' py', elem + ' pz',
                                                elem + ' p summed']})
        if Element(elem).block == 'd':
            options[elem].update({elem + ' d': [elem + ' dxz', elem + ' dyz', elem + ' dxy',
                                                elem + ' dx2-y2', elem + ' dz2', elem + ' d summed']})
    #    options.update({'Total':{'Total': None}})

    return options


@app.callback(Output('species_dropdown', 'options'),
              [Input('options', 'data')])
def set_elem_options(options):
    return [{'label': i, 'value': i} for i in options]


@app.callback(Output('orb_dropdown', 'options'),
              [Input('options', 'data'),
               Input('species_dropdown', 'value')])
def set_orb_options(options, selected_species):
    return [{'label': orb, 'value': orb}
            for sp in selected_species
            for orb in options[sp]]


@app.callback(Output('suborb_dropdown', 'options'),
              [Input('options', 'data'),
               Input('species_dropdown', 'value'),
               Input('orb_dropdown', 'value')])
def set_suborb_options(options, selected_species, selected_orb):
    return [{'label': suborb, 'value': suborb}
            for orb in selected_orb
            if orb.split()[0] in selected_species
            for suborb in options[orb.split()[0]][orb]]

@app.callback(Output('DOS_bands', 'figure'),
              [Input('submit_button', 'n_clicks'),
               Input('dos_object', 'data'),
               Input('bs_object', 'data')],
              #              [State('orb_dropdown', 'value')])
              [State('suborb_dropdown', 'value')])
def update_dosbandsfig(n_clicks, dos, bs, projlist):
    ## figure updates when the inputs change or the button is clicked
    ## figure does NOT update when elements or orbitals are selected
    ## de-serialize dos and bs from json format to pymatgen objects
    if dos:
        dos = CompleteDos.from_dict(json.loads(dos))
    if bs:
        bs = BandStructureSymmLine.from_dict(json.loads(bs))
    ## update the band structure and dos figure
    dosbandfig = BandsFig().generate_fig(dos, bs, projlist)
    return {'data':[dosbandfig]}