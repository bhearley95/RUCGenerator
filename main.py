# Import Modules
import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Import Functions
from Hexagonal.Hex1 import Hex1
from Hexagonal.Hex2 import Hex2
from Hexagonal.Hex3 import Hex3
from Square.Square1 import Square1
from Square.Square2 import Square2
from Square.Square3 import Square3
from Write.WriteCSV import WriteCSV
from Write.WriteRUC import WriteRUC
from Read.ReadCSV import ReadCSV
from Read.ReadRUC import ReadRUC

# Set the page configuration
st.set_page_config(layout="wide")

# Create the title
st.title("2D NASMAT RUC Generator")

# Create instructions
st.markdown('The 2D NASMAT RUC Generator is used to generate and visualize microstructres and corersponding *RUC files compatible with the NASA Mulitscale Analysis Tool (NASMAT). \n \n')

# Create tabs
tab1, tab2 = st.tabs(["Generator", "Visualizer"])

with tab1:
    # Create Header
    st.markdown("## RUC Generator")
    st.markdown('Generate a Representative Unit Cell (RUC) microstructure based on user-defined parameters. Select the microstructure type and input parameters to visualize and download the RUC data.')

    # Initialize the function
    func = None

    # Create columns for microstructure and definition selection
    col1, col2 = st.columns([1, 1])

    # Create input for microstructure type
    with col1:
        micro_opt = st.selectbox(
                "Select a microstructure:",
                [
                "Hexagonal", 
                "Square",
                ]
            )

    # Select definition option
    if micro_opt == "Hexagonal":

        # -- Create default values
        def_vals = {
                'VF':[1, 'float', 0.001, 0., math.pi / (2*math.sqrt(3)), 0.6],
                'R':[2, 'float', 0.001, 0., None, 10.],
                'NB':[1, 'int', 1, 1, None, 10],
                'NG':[2, 'int', 1, 1, None, 10],
                'F':[1,'int', 1, 1, None, 1],
                'M':[2,'int', 1, 1, None, 2],
                }

        # -- Create defintion list
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
        
    elif micro_opt == "Square":
        
        # -- Create default values
        def_vals = {
                'VF':[1, 'float', 0.001, 0., math.pi / 4, 0.6],
                'R':[2, 'float', 0.001, 0., None, 10.],
                'NB':[1, 'int', 1, 1, None, 10],
                'NG':[2, 'int', 1, 1, None, 10],
                'F':[1,'int', 1, 1, None, 1],
                'M':[2,'int', 1, 1, None, 2],
                }

        # -- Create defintion list
        def_list = {"Volume Fraction & Subcell Dimensions":{
                                                            'Inputs':['VF','NB','F','M'],
                                                            'Function':Square1
                                                            }, 
                    "Volume Fraction & Radius":{
                                                'Inputs':['VF','R','F','M'],
                                                'Function':Square2
                                                }, 
                    "Radius & Subcell Dimensions":{
                                                    'Inputs':['R','NB','F','M'],
                                                    'Function':Square3
                                                    }, 
                    }
        
    else:
        def_list = {}

    # Create definition selection
    with col2:
        def_opt = st.selectbox("Select an input type:", list(def_list.keys()))

    # Create input selection area
    st.markdown('''---''')

    # Create user inputs
    if def_opt:

        # Get the function and initalize values
        func = def_list[def_opt]['Function']
        values = {}

        # Separeate numeric inputs into two columns
        col3, col4 = st.columns([1, 1])

        # Create numeric inputs
        for key in def_vals.keys():

            # -- Determine column
            if def_vals[key][0] == 1:
                colnum = col3
            else:
                colnum = col4

            # -- Create the input
            with colnum:

                # -- Only initialize if it doesn't exist yet
                if f"num_input_{key}" not in st.session_state:
                    st.session_state[f"num_input_{key}"] = def_vals[key][5]

                if key in def_list[def_opt]['Inputs']:

                    # -- Set default value if previous was none
                    if st.session_state[f"num_input_{key}"] is None:
                        st.session_state[f"num_input_{key}"] = def_vals[key][5]

                    # -- Clamp previous value so it's within new min/max
                    val = st.session_state[f"num_input_{key}"]
                    try:
                        val = max(def_vals[key][3], min(def_vals[key][4], val))
                    except:
                        pass

                    # -- Pass the clamped value as value= to prevent reset
                    values[key] = st.number_input(
                        key,
                        key=f"num_input_{key}",
                        value=val,
                        step=def_vals[key][2],
                        min_value=def_vals[key][3],
                        max_value=def_vals[key][4]
                    )

                else:
                    # -- Remove existing value
                    st.session_state[f"num_input_{key}"] = None

                    # -- Create the disabled input
                    values[key] = st.number_input(
                                            key, 
                                            step = def_vals[key][2], 
                                            min_value = def_vals[key][3], 
                                            max_value = def_vals[key][4], 
                                            key = f"num_input_{key}",
                                            disabled=True
                                        )
                    

    # Generate and display the RUC
    if func is not None:

        # -- Create columns for organization
        col5, col6, col7, col8, col9 = st.columns([1, 1, 1, 1, 7])

        # -- Create the generate RUC button
        with col5:
            generate_clicked = st.button("Generate RUC", key = 'Gen_Button')

        # -- Create the gridline checkbox
        with col6:
            show_grid = st.checkbox("Show Grid Lines", value=True, key='Grid_Check')

        # -- Create fiber and matrix color selectors
        with col7:
            if 'fiber_color' not in st.session_state:
                st.session_state['fiber_color'] = 'blue'
            fib_color = st.selectbox(
                    "Fiber Color",
                    ["white", "black", "red", "green", "blue", "yellow", "purple"],
                    key = 'fiber_color'
                )
            
        with col8:
            if 'matrix_color' not in st.session_state:
                st.session_state['matrix_color'] = 'red'
            mat_color = st.selectbox(
                    "Matrix Color",
                    ["white", "black", "red", "green", "blue", "yellow", "purple"],
                    key = 'matrix_color'
                )

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
                colorscale=[[0, st.session_state['fiber_color']], [1, st.session_state['matrix_color']]],
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

            # Create columns for visualalization and data
            col10, col11, col12 = st.columns([1, 1, 4])

            # Display the microstruture
            with col10:
                st.plotly_chart(fig, width='content')

            # Create table with actual microstructure properties
            with col11:
                data = {'Property':['VF', 'R', 'NB', 'NG'],
                        'Value':[out['VF'], out['R'], out['NB'], out['NG']]}
                df = pd.DataFrame(data)
                st.dataframe(df) 

            # Create Files
            csv_data = WriteCSV(mask)
            ruc_data = WriteRUC(mask)

            # Create columns for downloading data
            col13, col14, col15 = st.columns([1, 1, 9])

            # Download to CSV
            with col13:
                st.download_button(
                    label="Download  CSV",
                    data=csv_data,
                    file_name="ruc.csv",
                    mime="text/csv"
                )

            # Download for *RUC
            with col14:
                st.download_button(
                label="Download *RUC File",
                data=ruc_data,
                file_name="ruc_data.txt",
                mime="text/plain"
            )
                
with tab2:
    # Create header
    st.markdown("## RUC Visualizer")
    st.markdown("Upload a CSV or *RUC file to visualize the microstructure.")

    # Set flag
    flag = 0

    # Allow file upload
    uploaded_file = st.file_uploader("Choose a file", type=["txt","mac","csv"], key = 'file_upload')

    # Read Data
    if uploaded_file is not None:
        # Read file as string (for text files)
        content = uploaded_file.read().decode("utf-8")

        # Read a csv file
        if uploaded_file.name.endswith('.csv'):
            try:
                mask, out = ReadCSV(content)
                st.session_state['mask_Viz'] = mask
                flag = 1
            except:
                st.error("Error reading CSV file. Please ensure it is formatted correctly.")

        else:
            #try:
                mask, out = ReadRUC(content)
                st.session_state['mask_Viz'] = mask
                flag = 1
            #except:
            #    st.error("Error reading *mac/*txt file. Please ensure it is formatted correctly and that the RUC is 2D.")

        # Display RUC
        if flag == 1:
            # -- Create columns for organization
            col6, col7, col8, col9 = st.columns([1, 1, 1, 8])

            # -- Create the gridline checkbox
            with col6:
                show_grid = st.checkbox("Show Grid Lines", value=True, key='Grid_Check_Viz')

            # -- Create fiber and matrix color selectors
            with col7:
                if 'fiber_color_Viz' not in st.session_state:
                    st.session_state['fiber_color_Viz'] = 'blue'
                fib_color = st.selectbox(
                        "Fiber Color",
                        ["white", "black", "red", "green", "blue", "yellow", "purple"],
                        key = 'fiber_color_Viz'
                    )
                
            with col8:
                if 'matrix_color_Viz' not in st.session_state:
                    st.session_state['matrix_color_Viz'] = 'red'
                mat_color = st.selectbox(
                        "Matrix Color",
                        ["white", "black", "red", "green", "blue", "yellow", "purple"],
                        key = 'matrix_color_Viz'
                    )

            # Only plot if we have a mask
            if 'mask_Viz' in st.session_state:
                mask = st.session_state['mask_Viz']

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
                    colorscale=[[0, st.session_state['fiber_color_Viz']], [1, st.session_state['matrix_color_Viz']]],
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

                # Create columns for visualalization and data
                col10, col11, col12 = st.columns([1, 1, 4])

                # Display the microstruture
                with col10:
                    st.plotly_chart(fig, width='content')

                # Create table with actual microstructure properties
                with col11:
                    data = {'Property':['VF', 'NB', 'NG'],
                            'Value':[out['VF'], out['NB'], out['NG']]}
                    df = pd.DataFrame(data)
                    st.dataframe(df) 

                # Create Files
                csv_data = WriteCSV(mask)
                ruc_data = WriteRUC(mask)

                # Create columns for downloading data
                col13, col14, col15 = st.columns([1, 1, 9])

                # Download to CSV
                with col13:
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name="ruc.csv",
                        mime="text/csv"
                    )

                # Download for *RUC
                with col14:
                    st.download_button(
                    label="Download *RUC File",
                    data=ruc_data,
                    file_name="ruc_data.txt",
                    mime="text/plain"
                )

   