# Import Modules
import math
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Import Functions
from Hexagonal.Hex1 import Hex1
from Hexagonal.Hex2 import Hex2
from Hexagonal.Hex3 import Hex3
from Write.WriteCSV import WriteCSV
from Write.WriteRUC import WriteRUC


# Set the page configuration
st.set_page_config(layout="wide")

# Create the Title
st.title("NASMAT RUC Generator")

# Create Instructions
st.markdown('The NASMAT RUC Generator is used to generate and visualize microstructres and corersponding *RUC files compatible with the NASA Mulitscale Analysis Tool (NASMAT). \n \n')
st.markdown('''---''')

# Initialize Data
func = None

# Create columns
col1, col2 = st.columns([1, 1])

# Select the desired micro structure
with col1:
    micro_opt = st.selectbox(
            "Select a microstructure:",
            [
            "Hexagonal", 
            #"Square",
            ]
        )

# Select definition option
if micro_opt == "Hexagonal":
    # Create default values
    def_vals = {
            'VF':[1, 'float', 0.001, 0., math.pi / (2*math.sqrt(3)), 0.6],
            'R':[2, 'float', 0.001, 0., None, 10.],
            'NB':[1, 'int', 1, 1, None, 10],
            'NG':[2, 'int', 1, 1, None, 10],
            'F':[1,'int', 1, 1, None, 1],
            'M':[2,'int', 1, 1, None, 2],
            }

    # Create defintion list
    def_list = {"Volume Fraction & Subcell Dimensions":{
                                                        'Inputs':['VF','NB','F','M'],
                                                        'Function':Hex1
                                                        }, 
                "Volume Fraction & Radius":{
                                            'Inputs':['VF','R','F','M'],
                                            'Function':Hex2
                                            }, 
                "Radius & Subcell Dimensions":{
                                                'Inputs':['R','NB','F','M'],
                                                'Function':Hex3
                                                }, 
                }
else:
    def_list = []

with col2:
    def_opt = st.selectbox("Select an input type:", list(def_list.keys()))

# Create user inputs
if def_opt:
    num_inputs = len(def_list[def_opt]['Inputs'])
    func = def_list[def_opt]['Function']
    values = {}

    # Create the numeric inputs
    col3, col4 = st.columns([1, 1])

    for key in def_vals.keys():
        if def_vals[key][0] == 1:
            colnum = col3
        else:
            colnum = col4

        with colnum:

            if f"num_input_{key}" not in st.session_state:
                st.session_state[f"num_input_{key}"] = def_vals[key][5]

            if key in def_list[def_opt]['Inputs']:
                if st.session_state[f"num_input_{key}"] == None:
                    st.session_state[f"num_input_{key}"] = def_vals[key][5]
                values[key] = st.number_input(key, 
                                        step = def_vals[key][2], 
                                        min_value = def_vals[key][3], 
                                        max_value = def_vals[key][4], 
                                        key = f"num_input_{key}"
                                    )
            else:
                st.session_state[f"num_input_{key}"] = None
                values[key] = st.number_input(key, 
                                        step = def_vals[key][2], 
                                        min_value = def_vals[key][3], 
                                        max_value = def_vals[key][4], 
                                        key = f"num_input_{key}",
                                        disabled=True
                                )

if func is not None:

    # Create columns
    col5, col6, col7 = st.columns([1, 1, 9])

    with col5:
        generate_clicked = st.button("Generate RUC", key = 'Gen_Button')

    with col6:
        show_grid = st.checkbox("Show Grid Lines", value=True, key='Grid_Check')

    # If generate is clicked, run function and save mask in session_state
    if generate_clicked:
        func_values = {}
        flag = 0
        for key in values.keys():
            if key in def_list[def_opt]['Inputs']:
                func_values[key] = values[key]
        st.session_state['mask'] = func(**func_values)

    # Only plot if we have a mask
    if 'mask' in st.session_state:
        mask, out = st.session_state['mask']

        # Decide on grid spacing
        if show_grid:
            xgap = 0.5
            ygap = 0.5
        else:
            xgap = None
            ygap = None

        # Create Plotly figure
        fig = go.Figure(data=go.Heatmap(
            z=mask,
            colorscale=[[0, 'blue'], [1, 'red']],
            showscale=False,
            xgap=xgap,
            ygap=ygap
        ))

        # Layout tweaks
        fig.update_layout(
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, scaleanchor="y", constrain='domain'),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, autorange='reversed', scaleanchor="x"),
            margin=dict(l=0, r=0, t=0, b=0)
        )

        # Create columns
        col8, col9, col10 = st.columns([1, 1, 4])

        with col8:
            # Display in Streamlit
            st.plotly_chart(fig, width='content')

        with col9:
            data = {'Property':['VF', 'R', 'NB', 'NG'],
                    'Value':[out['VF'], out['R'], out['NB'], out['NG']]}
            df = pd.DataFrame(data)
            st.dataframe(df) 

        # Create Files
        csv_data = WriteCSV(mask)
        ruc_data = WriteRUC(mask)

        col11, col12, col13 = st.columns([1, 1, 9])
        with col11:
            st.download_button(
                label="Download  CSV",
                data=csv_data,
                file_name="ruc.csv",
                mime="text/csv"
            )

        with col12:
            st.download_button(
            label="Download *RUC File",
            data=ruc_data,
            file_name="ruc_data.txt",
            mime="text/plain"
        )