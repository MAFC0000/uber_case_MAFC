import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PowerTransformer, FunctionTransformer, OneHotEncoder

# Function to join multiple classes
def feature_map_categories_courier_flow(X):
    series = pd.Series(X.values.ravel())

    rare_classes = ['UberX', 'Fleet', 'SUV', 'Onboarder'] 
    new_name = 'UberX_Fleet_SUV_Onboarder'
    
    series_mapped = series.apply(lambda x: new_name if x in rare_classes else x)
    return series_mapped.to_numpy().reshape(-1, 1)

# Function to join multiple classes
def feature_map_categories_archetype(X):
    series = pd.Series(X.values.ravel())
    
    rare_classes = ['Build experience', 'Unspecified', 'Unlaunched'] 
    new_name = 'Build experience_Unspecified_Unlaunched'
    
    series_mapped = series.apply(lambda x: new_name if x in rare_classes else x)
    return series_mapped.to_numpy().reshape(-1, 1)

# Function to map the average velocity per territory
def feature_territory_average_velocity(X):
    territory_map = {
        'Central': 0.1187,
        'Long Tail - Region': 0.1567,
        'North': .1715,
        'South East': .1665,
        'West': .1725
    }
    
    series = pd.Series(X.values.ravel())
    series_mapped = series.map(territory_map)

    return series_mapped.to_numpy().reshape(-1, 1)

# Function to convert the hours in radian hours
def feature_hour_cyclical(X):
    series = X.values.ravel()
    hour_radians = 2 * np.pi * series / 24
    
    hour_sin = np.sin(hour_radians)
    hour_cos = np.cos(hour_radians)
    
    X_transformed = np.c_[hour_sin, hour_cos]
    
    return X_transformed

# Function to convert the days in radian days
def feature_day_cyclical(X):
    series = X.values.ravel()
    day_radians = 2 * np.pi * series / 7
    
    day_sin = np.sin(day_radians).reshape(-1, 1)
    day_cos = np.cos(day_radians).reshape(-1, 1)
    
    X_transformed = np.c_[day_sin, day_cos]
    
    return X_transformed

#Creating pipeline
def columns_transformer():
    territory_pipe = Pipeline(steps=[('Velocity', FunctionTransformer(func=feature_territory_average_velocity, feature_names_out='one-to-one', validate=False))])
    courier_flow_pipe = Pipeline(steps=[('MapCategories', FunctionTransformer(func=feature_map_categories_courier_flow, feature_names_out='one-to-one', validate=False)),
                                        ('OneHot', OneHotEncoder(sparse_output=False, drop='first'))])
    archetype_pipe = Pipeline(steps=[('MapCategories', FunctionTransformer(func=feature_map_categories_archetype, feature_names_out='one-to-one', validate=False)),
                                        ('OneHot', OneHotEncoder(sparse_output=False, drop='first'))])
    merchant_pipe = Pipeline(steps=[('OneHot', OneHotEncoder(sparse_output=False, drop='first'))])
    day_pipeline = Pipeline(steps=[('DayConverter', FunctionTransformer(func=feature_day_cyclical, feature_names_out='one-to-one', validate=False))])
    hour_pipeline = Pipeline(steps=[('HourConverter', FunctionTransformer(func=feature_hour_cyclical, feature_names_out='one-to-one', validate=False))])
    distances_pipeline = Pipeline(steps=[('Normalize and Standardize', PowerTransformer(method='yeo-johnson', standardize=True))])

    #Transformador final
    columnasTransformer = ColumnTransformer(transformers = [('territory', territory_pipe, ['territory']),
                                                            ('courier_flow', courier_flow_pipe, ['courier_flow']),
                                                            ('geo_archetype', archetype_pipe, ['geo_archetype']),
                                                            ('merchant_surface', merchant_pipe, ['merchant_surface']),
                                                            ('weekday', day_pipeline, ['weekday']),
                                                            ('hour_of_day', hour_pipeline, ['hour_of_day']),
                                                            ('distances', distances_pipeline, ['pickup_distance', 'dropoff_distance'])],
                                            remainder='passthrough') 
    return columnasTransformer
