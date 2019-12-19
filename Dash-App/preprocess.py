import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from functools import reduce

def local_time(time, zone):
    # This function takes input fo a datetime column and a timezone column to compute the local_time after timezone and daylight
    # savings adjustments have been applied.
    z = zone[3:]
    operator = z[0]
    hour = z[1:3]
    minute = z[3:]
    dt = time + timedelta(hours = int(operator + hour)) + timedelta(minutes = int(operator + minute))
    return dt

def preprocess(dataframe, utc = False, offset_time = False):
    #This function takes as input a dataframe class object for the Health Project. It preprocesses the features by dropping NULL columns, adjusting column names, casts
    #features into the appropriate datatype and creates features based on the columns of the dataframe. The 'utc' variable specifies if the datetime columns are in UTC milliseconds
    #or a in a proper datatime format. The "offset_time" specifies if an adjustment of timezone and daylight savings time should be applied based on the values of the time_offset
    #feature in the dataframe.

    dataframe = dataframe.copy()
    dataframe = dataframe.dropna(how = 'all', axis = 1)
    dataframe.columns = [x.split('.')[-1] for x in dataframe.columns]

    weekend = ['Saturday', 'Sunday']
    time_cols = ['create_time', 'start_time', 'end_time']
    time_cols = [x for x in time_cols if x in dataframe.columns]

    if ('day_time' in dataframe.columns) & (utc == True):
        time_cols = ['create_time']
        dataframe['create_time'] = dataframe['day_time']


    exercise_dict = {0: 'Custom', 1001: 'Walking', 1002: 'Running', 11007: 'Circut Training',
                 13001: 'Hiking' , 14001: 'Swimming', 15006: 'Elliptical'}

    if utc == True:
        for name in time_cols:
            dataframe[name] = (dataframe[name]/1000).apply(datetime.utcfromtimestamp)
    else: 
        for name in time_cols:
            dataframe[name] = pd.to_datetime(dataframe[name])

    if offset_time == True:
        for name in time_cols:
            dataframe[name] = dataframe.apply(lambda row: local_time(row[name], row['time_offset']), axis=1)
        
    dataframe['date'] = dataframe['create_time'].dt.date

    for name in time_cols:
        hour_name = name[:-4] + 'hour'
        dataframe[hour_name] = dataframe[name].dt.hour

    dataframe['weekday'] = pd.Categorical(dataframe['create_time'].dt.weekday_name, 
                                        categories = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday'],
                                         ordered = True)
    dataframe['day_label'] = ['weekend' if (x in weekend) else 'weekday' for x in dataframe['weekday']]

    if ('duration' not in dataframe.columns) & ('start_time' in dataframe.columns) & ('end_time' in dataframe.columns):
        dataframe['duration'] = (dataframe['end_time'] - dataframe['start_time']).dt.total_seconds()/3600
    elif 'duration' in dataframe.columns:
        dataframe['duration'] = dataframe['duration']/1000/60
    else:
        pass

    if 'exercise_type' in dataframe.columns:
        dataframe['exercise_type'] = dataframe['exercise_type'].map(exercise_dict)
        speed_cutoff = 1.34
        distance_cutoff = 2000
        dataframe.loc[(dataframe['exercise_type'] == 'Walking') & (dataframe['mean_speed'] >= speed_cutoff) & (dataframe['distance']>=distance_cutoff), 'exercise_type'] = 'Brisk Walking'

    return dataframe

def merge(df_list):
    new_list = []
    cols_list = ['sleep', 'exercise', 'calorie', 'stress', 'steps', 'heart_rate']
    cols = {'sleep': ['date', 'duration', 'efficiency'],
            'exercise': ['date', 'duration'],
            'calorie': ['date', 'active_calorie', 'rest_calorie'],
            'stress': ['date', 'score'],
            'steps': ['date', 'count'],
            'heart_rate': ['date', 'heart_rate']
            }
    for i in range(len(df_list)):
        df2 = df_list[i].copy()
        df2 = df2[cols[cols_list[i]]]
        new_list.append(df2)

    df_final = reduce(lambda left, right: pd.merge(left, right, on = 'date', how = 'outer'), new_list)
    df_final = df_final.rename({'duration_x': 'sleep_duration', 'duration_y': 'exercise_duration', 'efficiency': 'sleep_efficiency',
                            'score': 'stress_score', 'count': 'step_count'}, axis = 1)
    return df_final
        