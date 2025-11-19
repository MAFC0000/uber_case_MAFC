import pandas as pd
import numpy as np

# Function to prepare descriptive data
def des_prepare_data_function():
    
    # Loading data
    df = pd.read_csv('../BC_A&A_with_ATD.csv', sep=',')

    # Filtering columns with null or zero values
    print('Initial df.shape:', df.shape)
    df = df.replace('\\N', np.nan)
    df = df.dropna(how='any')
    print('After filtering \\N values, df.shape:', df.shape)
    df = df[df['pickup_distance']!='0']
    df = df[df['dropoff_distance']!='0']
    print('After filtering zero distances, df.shape:', df.shape)

    # Formatting columns
    str_float_columns = {
        'region': str,
        'territory': str,
        'country_name': str,
        'workflow_uuid': str,
        'driver_uuid': str,
        'delivery_trip_uuid': str,
        'courier_flow': str,
        'geo_archetype': str,
        'merchant_surface': str,
        'pickup_distance': float,
        'dropoff_distance': float,
        'ATD': float}

    date_columns = ['restaurant_offered_timestamp_utc', 
                    'order_final_state_timestamp_local', 
                    'eater_request_timestamp_local']

    df = df.astype(str_float_columns)

    df['restaurant_offered_timestamp_utc'] = (df['restaurant_offered_timestamp_utc'].str.replace('.000', '', regex=False)) # Removing milliseconds for uniformity
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
    df['ATD'] = np.round(df['ATD'], 2)
    df['weekday'] = df['eater_request_timestamp_local'].dt.day_name()
    df['hour_of_day'] = df['eater_request_timestamp_local'].dt.hour
    
    return df