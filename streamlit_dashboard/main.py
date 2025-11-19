from datetime import date
import streamlit as st
from historical_performance_functions.des_prepare_data import des_prepare_data_function
from historical_performance_functions.des_kpis_and_visuals import des_kpi_total_function, des_kpi_atd_function, des_kpi_velocity_function, des_visuals_day_bars, des_visuals_stacked_bar, des_visuals_pie, des_visuals_archetype_scatterplot, des_visuals_territory_scatterplot, des_visuals_table, des_initial_graph_prediction_function, des_initial_graph_function, des_visuals_hour_bars
import pandas as pd
from st_aggrid import AgGrid
import joblib
import pandas as pd
import sys
from atd_prediction.pred_additional_functions import pred_feature_importances_table

# General page configuration
st.set_page_config(
    layout="wide",
    page_title="ATD Dashboard")

# Definition of internal functions to load descriptive data with caching to optimize performance
@st.cache_data
def load_data():
    return des_prepare_data_function()

# Loading the models
sys.path.append("atd_prediction")

@st.cache_resource
def y_transform():
    model = joblib.load('atd_prediction/y_target_transformer.joblib')
    return model
model_y = y_transform()

@st.cache_resource
def load_rf_model():
    model = joblib.load('atd_prediction/atd_prediction_model_rf.joblib')
    return model
model_rf = load_rf_model()

@st.cache_resource
def load_rf_gs():
    gs = joblib.load('atd_prediction/atd_prediction_grid_search_rf.joblib')
    return gs
gs_rf = load_rf_gs()

@st.cache_resource
def load_xgb_model():
    model = joblib.load('atd_prediction/atd_prediction_model_xgb.joblib')
    return model
model_xgb = load_xgb_model()

@st.cache_resource
def load_xgb_gs():
    gs = joblib.load('atd_prediction/atd_prediction_grid_search_xgb.joblib')
    return gs
gs_xgb = load_xgb_gs()

@st.cache_resource
def load_mlp_model():
    model = joblib.load('atd_prediction/atd_prediction_model_mlp.joblib')
    return model
model_mlp = load_mlp_model()

@st.cache_resource
def load_mlp_gs():
    gs = joblib.load('atd_prediction/atd_prediction_grid_search_mlp.joblib')
    return gs
gs_mlp = load_mlp_gs()

@st.cache_resource
def load_features_importance():
    imp = joblib.load('atd_prediction/df_importances.joblib')
    return imp
imp_df = load_features_importance()

# Main menu
st.title("Let's drive decisions!")

page=st.selectbox('What hidden insights will you unlock today?', ['Historical performance','ATD prediction'])

st.divider()
st.sidebar.markdown(f"{page} filters")

# Descriptive analytics page
if page=='Historical performance':
    st.subheader("Historical performance")
    
    # Filters selection
    des_territory=st.sidebar.multiselect('Territory',['South East', 'Central', 'Long Tail - Region', 'West', 'North'])
    des_courier_flow=st.sidebar.multiselect('Courier Flow',['Motorbike', 'UberEats', 'Logistics', 'Fleet', 'Onboarder', 'SUV', 'UberX'])
    des_geo_archetype=st.sidebar.multiselect('Geography archetype',['Build experience', 'Drive momentum', 'Play offense', 'Defend CP', 'Unlaunched', 'Unspecified'])
    des_merchant_surface=st.sidebar.multiselect('Merchant Surface',['Other', 'POS', 'Tablet', 'Unspecified', 'Web/Mobile'])
    des_initial_date, des_final_date = st.sidebar.date_input('Eater request date range',value=(date(2025, 3, 1), date(2025, 4, 27)), min_value=(date(2025, 3, 1)), max_value=(date(2025, 4, 30)))
    
    # Data loading and filtering according to user input
    df=load_data()
    try:
        if des_territory!=[]:
            df=df[df['territory'].isin(des_territory)]
        if des_courier_flow!=[]:
            df=df[df['courier_flow'].isin(des_courier_flow)]
        if des_geo_archetype!=[]:
            df=df[df['geo_archetype'].isin(des_geo_archetype)]
        if des_merchant_surface!=[]:
            df=df[df['merchant_surface'].isin(des_merchant_surface)]
        df=df[(df['eater_request_timestamp_local'].dt.date >=pd.to_datetime(des_initial_date).date()) & (df['eater_request_timestamp_local'].dt.date <=pd.to_datetime(des_final_date).date())]
    except Exception as e:
        st.error(f"An error occurred while filtering the data: {e}\n Please check your filter selections.")
    
    # Initial trend graph
    st.markdown('The actual trend is:')
    try:
        graph=des_initial_graph_prediction_function(df[['delivery_trip_uuid', 'eater_request_timestamp_local', 'ATD']])
        st.pyplot(graph)
    except Exception as e:
        graph=des_initial_graph_function(df[['delivery_trip_uuid', 'eater_request_timestamp_local', 'ATD']])
        st.pyplot(graph)
    
    # KPIs calculation and display
    des_kpi_total = des_kpi_total_function(df['delivery_trip_uuid'])
    des_kpi_atd = des_kpi_atd_function(df['ATD'])
    des_kpi_velocity= des_kpi_velocity_function(df['pickup_distance'], df['dropoff_distance'], df['ATD'])

    kpi_1, kpi_2, kpi_3 = st.columns(3) 

    with kpi_1:
        st.metric(label="Total deliveries",value=f"{des_kpi_total:,.0f}")
        st.caption("Trip UUIDs count")

    with kpi_2:
        st.metric(label="ATD Median (Min)",value=des_kpi_atd)
        st.caption("ATD Median (Min)")

    with kpi_3:
        st.metric(label="Velocity median (Km/Min)",value=des_kpi_velocity)
        st.caption("Total distance (Km) / ATD (Min) median")
    
    # Graphs and visuals display
    graph_1, graph_2, graph_3 = st.columns([2, 2, 2])
    
    with graph_1:
        st.markdown("ATD vs Total distance by archetype")
        graph=des_visuals_archetype_scatterplot(df[['geo_archetype','delivery_trip_uuid','pickup_distance','dropoff_distance','ATD']])
        st.pyplot(graph)

    with graph_2:
        st.markdown("ATD vs Total distance by territory")
        graph=des_visuals_territory_scatterplot(df[['territory','delivery_trip_uuid','pickup_distance','dropoff_distance','ATD']])
        st.pyplot(graph)
    
    with graph_3:
        st.markdown("Archetype total deliveries by territory")
        graph=des_visuals_stacked_bar(df[['territory','geo_archetype']])
        st.pyplot(graph)
    
    graph_4, graph_5= st.columns([1, 1])
    with graph_4:
        st.markdown("Weekday analysis")
        graph=des_visuals_day_bars(df[['weekday','ATD', 'driver_uuid']])
        st.pyplot(graph)

    with graph_5:
        st.markdown("Summary table")
        summarized_df=des_visuals_table(df[['delivery_trip_uuid','geo_archetype','territory','courier_flow','ATD','pickup_distance','dropoff_distance']])
        AgGrid(summarized_df, height=620)
    
    graph_6, graph_7 = st.columns([4, 1])
    
    with graph_6:
        st.markdown("Hour analysis")
        graph=des_visuals_hour_bars(df[['hour_of_day','ATD']])
        st.pyplot(graph)
    
    with graph_7:
        st.markdown("Deliveries by courier flow")
        graph=des_visuals_pie(df[['courier_flow']])
        st.pyplot(graph)

if page=='ATD prediction':
    st.subheader("ATD prediction")
    
    # Filters selection
    var_territory=st.sidebar.multiselect('Territory',['South East', 'Central', 'Long Tail - Region', 'West', 'North'])
    var_courier_flow=st.sidebar.multiselect('Courier Flow',['Motorbike', 'UberEats', 'Logistics', 'Fleet', 'Onboarder', 'SUV', 'UberX'])
    var_geo_archetype=st.sidebar.multiselect('Geography archetype',['Build experience', 'Drive momentum', 'Play offense', 'Defend CP', 'Unlaunched', 'Unspecified'])
    var_merchant=st.sidebar.multiselect('Merchant Surface',['Other', 'POS', 'Tablet', 'Unspecified', 'Web/Mobile'])
    var_weekday=st.sidebar.slider(label='Weekday (0-Monday, ... ,6-Sunday)', min_value=0, max_value=6)
    var_hour=st.sidebar.slider(label='Hour', min_value=0, max_value=23)
    var_pickup_distance=st.sidebar.slider(label='Pickup distance', min_value=0,  max_value=10)
    var_dropoff_distance=st.sidebar.slider(label='Dropoff distance', min_value=0, max_value=20)
    
    if st.button('Predict'):
    # Input data
        input_df = pd.DataFrame({
                'territory': var_territory,
                'courier_flow': var_courier_flow,   
                'geo_archetype': var_geo_archetype, 
                'merchant_surface': var_merchant,        
                'pickup_distance': var_weekday,
                'dropoff_distance': var_hour, 
                'weekday': var_pickup_distance,
                'hour_of_day': var_dropoff_distance
            })
        
        st.markdown("Predictions")
        rf, xgb, mlp = st.columns(3) 

        with rf:
            prediction = model_rf.predict(input_df)[0]
            final_prediction = model_y.inverse_transform(prediction.reshape(-1, 1))[0][0]
            
            error=gs_rf.best_score_
            final_error = model_y.inverse_transform(error.reshape(-1,1))[0][0]
            
            st.metric(label="Random forest",
                      value= f"{final_prediction: .2f} minutes",
                      delta= f"RMSE: {final_error: .2f}",
                      delta_color="off")
            
        with xgb:
            prediction = model_xgb.predict(input_df)[0]
            final_prediction = model_y.inverse_transform(prediction.reshape(-1, 1))[0][0]
            
            error=gs_xgb.best_score_
            final_error = model_y.inverse_transform(error.reshape(-1,1))[0][0]
            
            st.metric(label="XGBoost",
                      value= f"{final_prediction: .2f} minutes",
                      delta= f"RMSE: {final_error: .2f}",
                      delta_color="off")
            
        with mlp:
            prediction = model_mlp.predict(input_df)[0]
            final_prediction = model_y.inverse_transform(prediction.reshape(-1, 1))[0][0]
            
            error=gs_mlp.best_score_
            final_error = model_y.inverse_transform(error.reshape(-1,1))[0][0]
            
            st.metric(label="Multilayer Neural Network",
                      value= f"{final_prediction: .2f} minutes",
                      delta= f"RMSE: {final_error: .2f}",
                      delta_color="off")
    st.divider()
    st.markdown("XGBoost feature importance")
    graph = pred_feature_importances_table(imp_df)
    st.pyplot(graph)
        
        


# st.title ("this is the app title")
# st.header("this is the markdown")
# st.markdown("this is the header")
# st.subheader("this is the subheader")
# st.caption("this is the caption")
# st.code("x=2021")
# st.latex(r''' a+a r^1+a r^2+a r^3 ''')
# st.checkbox('yes')
# st.button('Click')
# st.radio('Pick your gender',['Male','Female'])
# st.selectbox('Pick your gender',['Male','Female'])
# st.multiselect('choose a planet',['Jupiter', 'Mars', 'neptune'])
# st.select_slider('Pick a mark', ['Bad', 'Good', 'Excellent'])
# st.slider('Pick a number', 0,50)
# st.number_input('Pick a number', 0,10)
# st.text_input('Email address')
# st.date_input('Travelling date')
# st.time_input('School time')
# st.text_area('Description')
# st.color_picker('Choose your favorite color')
# st.header("Segunda Sección")
# st.divider()
# st.text("Contenido de la segunda sección.")


# st.markdown(f"**Territory:** {des_territory}")
# st.markdown(f"**Courier Flow:** {des_courier_flow}")
# st.markdown(f"**Geo Archetype:** {des_geo_archetype}")
# st.markdown(f"**Merchant Surface:** {des_merchant_surface}")
# st.markdown(f"**Date Initial:** {des_initial_date}")
# st.markdown(f"**Date Final:** {des_final_date}")
