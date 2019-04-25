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


def read_data(historical_data_dir, future_data_dir, hist_year, current_timestep, scenario):
    #files
    file_wind = "wss__"+scenario+".csv"
    file_solar = "rsds__"+scenario+".csv"
    file_historic = "weather_hist_hourly_"+str(hist_year)+".csv"

    #main data frames - historic all and daily all (includes all years)
    weather_hist = pd.read_csv(historical_data_dir+os.path.sep+file_historic)
    wind_daily_all = pd.read_csv(future_data_dir+os.path.sep+file_wind)
    solar_daily_all = pd.read_csv(future_data_dir+os.path.sep+file_solar)

    #historic wind and solar
    wind_hist = weather_hist[weather_hist.parameter == 'wind']
    solar_hist = weather_hist[weather_hist.parameter == 'insolation']

    #daily wind and solar
    wind_daily = wind_daily_all[wind_daily_all.timestep == current_timestep]
    solar_daily = solar_daily_all[solar_daily_all.timestep == current_timestep]

    #------ Get Wind Speed for the sim year -------------
    #calculate daily mean of historic wind
    wind_day_av = wind_hist.groupby(["day","region"]).mean()["value"].reset_index()

    #create key of [day_region]
    list_values = (wind_hist["day"].astype(str)+"_"+wind_hist["region"].astype(str)).values #hourly historic data
    wind_hist["key"] =  list_values

    list_values2 = (wind_day_av["day"].astype(str)+"_"+wind_day_av["region"].astype(str)).values #daily averaged set of historic data
    wind_day_av["key"] =  list_values2

    list_values3 = (wind_daily["yearday"].astype(str)+"_"+wind_daily["region"].astype(str)).values #daily data from weather@home
    wind_daily["key"] =  list_values3

    #merge historic hourly data and historic averaged data
    wind_norm = wind_hist.merge(wind_day_av,how='left',on="key",suffixes=('_h','_d'))

    #normalise hourly values
    wind_norm["value"] = wind_norm["value_h"]/wind_norm["value_d"]  # normalised value = (hourly value)/(daily mean)

    #drop columns
    wind_norm.drop(["id","year","region_h","parameter","value_h","day_d","region_d","value_d"],axis = 1, inplace=True)

    #merge nomalised hourly data and weather@home daily data
    wind_speed = wind_norm.merge(wind_daily,how='left',on="key")
    wind_speed["value"] = wind_speed["value"]*wind_speed["wss"]  #houlr value = (normalised hourly value)*(daily mean)

    #cleaning data frame
    wind_speed.drop(["day_h","key","wss",],axis = 1, inplace=True)
    wind_speed.rename(columns={"timestep":"year", "yearday":"day"}, inplace=True)


   #------ Get insolation for the sim year -------------
    #calculate daily mean of historic wind
    solar_day_av = solar_hist.groupby(["day","region"]).mean()["value"].reset_index()

    #create key of [day_region]
    list_values = (solar_hist["day"].astype(str)+"_"+solar_hist["region"].astype(str)).values #hourly historic data
    solar_hist["key"] =  list_values

    list_values2 = (solar_day_av["day"].astype(str)+"_"+solar_day_av["region"].astype(str)).values #daily averaged set of historic data
    solar_day_av["key"] =  list_values2

    list_values3 = (solar_daily["yearday"].astype(str)+"_"+solar_daily["region"].astype(str)).values #daily data from weather@home
    solar_daily["key"] =  list_values3

    #merge historic hourly data and historic averaged data
    solar_norm = solar_hist.merge(solar_day_av,how='left',on="key",suffixes=('_h','_d'))

    #normalise hourly values
    solar_norm["value"] = solar_norm["value_h"]/solar_norm["value_d"]  # normalised value = (hourly value)/(daily mean)

    #drop columns
    solar_norm.drop(["id","year","region_h","parameter","value_h","day_d","region_d","value_d"],axis = 1, inplace=True)

    #merge nomalised hourly data and weather@home daily data
    solar_insolation = solar_norm.merge(solar_daily,how='left',on="key")
    solar_insolation["value"] = solar_insolation["value"]*solar_insolation["rsds"]  #houlr value = (normalised hourly value)*(daily mean)

    #cleaning data frame
    solar_insolation.drop(["day_h","key","rsds",],axis = 1, inplace=True)
    solar_insolation.rename(columns={"timestep":"year", "yearday":"day"}, inplace=True)


    # input_parameter names based on historic data year and weather scenario
    wind_param = "wind_"+str(hist_year)+"_"+scenario # ex : "wind_2010_NF1"
    insolation_param = "insolation_"+str(hist_year)+"_"+scenario     # ex : "insolation_2010_NF1"

    #integrating paramters to data frames,
    solar_insolation["parameter"] = insolation_param
    wind_speed ["parameter"] = wind_param

    #reorder columns,
    col_order = ["year","day","hour","region","parameter","value"]

    wind_speed = wind_speed[col_order]
    solar_insolation = solar_insolation[col_order]

    return (wind_speed,solar_insolation)


def write_data(input_parameters,wind_speed,solar_insolation):
    #write input parameters to input_parameters table

    #convert the yearly data to match seasonal_weeks

    #write the converted data to input_timestep table

    return
