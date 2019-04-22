"""
Outline :
1. Read climate data from nismod2/data/scenarios/climate/ (rsds_NF1.csv -solar irradiation) aand (wss_NF1.csv - wind speed)
2. Read historic weather data from data/energy_supply/scenarios/weather_hist_hourly.csv
3. Wind speed height conversion (moved to supply model)
4. Average historic weather data and get daily average 
5. Noramlise historic weather data using dauly average values from step 4.
6. Generate hourly weather data (weather@home data)
7. Set input_parameters 
8. Write data to input_paramter and then input_timestep tables.

"""
import os
import numpy as np 
import pandas as pd 

hist_year = 2010
current_timestep = 2020 #how to get this ?
scenario = 1

def read_data(hist_year, current_timestep, scenario):
       
    #path to files
    hist_data =  'C:\\Users\Lahiru Jayasuriya\\Desktop\\NISMOD\\nismod2\\data\\energy_supply\\scenarios'
    weather_data = 'C:\\Users\\Lahiru Jayasuriya\\Desktop\\NISMOD\\nismod2\\data\\scenarios\\climate'

    #files
    file_wind = "wss__NF"+str(scenario)+".csv"
    file_solar = "rsds__NF"+str(scenario)+".csv"
    file_historic = "weather_hist_hourly_"+str(hist_year)+".csv"

    weather_hist = pd.read_csv(hist_data+os.path.sep+file_historic)
    wind_daily = pd.read_csv(weather_data+os.path.sep+file_wind)
    solar_daily = pd.read_csv(weather_data+os.path.sep+file_solar)

    return (weather_hist, wind_daily, solar_daily)

def daily_mean_hist(weather_hist):

    wind_hist = weather_hist[weather_hist.parameter == 'wind']
    solar_hist = weather_hist[weather_hist.parameter == 'insolation']
            
