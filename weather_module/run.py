"""
Outline :
1. Read climate data from nismod2/data/scenarios/climate/ (rsds_NF1.csv -solar irradiation) and
   (wss_NF1.csv - wind speed)
2. Read historic weather data from data/energy_supply/scenarios/weather_hist_hourly.csv
3. Wind speed height conversion (moved to supply model)
4. Average historic weather data and get daily average
5. Noramlise historic weather data using dauly average values from step 4.
6. Generate hourly weather data (weather@home data)
7. Set input_parameters
8. Write data to input_paramter and then input_timestep tables.

"""
import os

import pandas as pd


def read_data(historical_data_dir, future_data_dir, historical_year, current_year, scenario):
    """Read historical and future data
    """
    # files
    file_wind = "wss__{}.csv".format(scenario)
    file_solar = "rsds__{}.csv".format(scenario)
    file_historic = "weather_hist_hourly_{}.csv".format(historical_year)

    # main data frames - historic all and daily all (includes all years)
    weather_hist = pd.read_csv(os.path.join(historical_data_dir, file_historic))
    wind_daily_all = pd.read_csv(os.path.join(future_data_dir, file_wind))
    solar_daily_all = pd.read_csv(os.path.join(future_data_dir, file_solar))

    # historic wind and solar
    wind_hist = weather_hist[weather_hist.parameter == 'wind']
    solar_hist = weather_hist[weather_hist.parameter == 'insolation']

    # daily wind and solar
    wind_daily = wind_daily_all[wind_daily_all.timestep == current_year]
    solar_daily = solar_daily_all[solar_daily_all.timestep == current_year]

    return wind_daily, wind_hist, solar_daily, solar_hist

def calculate_daily_average(data):
    """(day, region, hour, value) => (day, region, value)
    """
    return data.groupby(['day', 'region']).mean()['value'].reset_index()


def normalise_hourly(data, daily_average):
    """(day, region, hour, value), (day, region, value) => (day, region, hour, value)
    """
    # merge historic hourly data and historic averaged data
    normalised = data.merge(
        daily_average, how='left', on=['day', 'region'], suffixes=('_h', '_d'))

    # normalise hourly values = (hourly value) / (daily mean)
    normalised["value"] = normalised.value_h / normalised.value_d

    # drop columns
    normalised.drop(
        ["id", "year", "region_h", "parameter", "value_h", "day_d", "region_d", "value_d"],
        axis=1, inplace=True)


def project_hourly(historical_normalised, future):
    # merge normalised hourly data and weather@home daily data
    merged = historical_normalised.merge(future, how='left', on=['day', 'region'])
    # hourly value = (normalised hourly value) * (daily mean)
    merged["value"] = merged.value * merged.wss

    #cleaning data frame
    merged.drop(["day_h", "key", "wss"], axis=1, inplace=True)
    merged.rename(columns={"timestep":"year", "yearday":"day"}, inplace=True)


def solar_rest(solar_hist, solar_daily, historical_year, scenario, wind_speed):
    #
    # Get insolation for the sim year
    #

    # calculate daily mean of historic wind
    solar_day_av = solar_hist.groupby(["day", "region"]).mean()["value"].reset_index()

    # create key of [day_region]
    # hourly historic data
    list_values = (
        solar_hist["day"].astype(str) + "_" + solar_hist["region"].astype(str)).values
    solar_hist["key"] = list_values

    # daily averaged set of historic data
    list_values2 = (
        solar_day_av["day"].astype(str) + "_" + solar_day_av["region"].astype(str)).values
    solar_day_av["key"] = list_values2

    # daily data from weather@home
    list_values3 = (
        solar_daily["yearday"].astype(str) + "_" + solar_daily["region"].astype(str)).values
    solar_daily["key"] = list_values3

    # merge historic hourly data and historic averaged data
    solar_norm = solar_hist.merge(solar_day_av, how='left', on="key", suffixes=('_h', '_d'))

    # normalise hourly values
    # normalised value = (hourly value)/(daily mean)
    solar_norm["value"] = solar_norm["value_h"] / solar_norm["value_d"]

    # drop columns
    solar_norm.drop(
        ["id", "year", "region_h", "parameter", "value_h", "day_d", "region_d", "value_d"],
        axis=1, inplace=True)

    # merge nomalised hourly data and weather@home daily data
    # hourly value = (normalised hourly value) * (daily mean)
    solar_insolation = solar_norm.merge(solar_daily, how='left', on="key")
    solar_insolation["value"] = solar_insolation["value"] * solar_insolation["rsds"]

    # cleaning data frame
    solar_insolation.drop(["day_h", "key", "rsds"], axis=1, inplace=True)
    solar_insolation.rename(columns={"timestep":"year", "yearday":"day"}, inplace=True)


    # input_parameter names based on historic data year and weather scenario
    # e.g. "wind_2010_NF1"
    wind_param = "wind_{}_{}".format(historical_year, scenario)
    # e.g. "insolation_2010_NF1"
    insolation_param = "insolation_{}_{}".format(historical_year, scenario)

    # integrating paramters to data frames,
    solar_insolation["parameter"] = insolation_param
    wind_speed["parameter"] = wind_param

    # reorder columns,
    col_order = ["year", "day", "hour", "region", "parameter", "value"]

    wind_speed = wind_speed[col_order]
    solar_insolation = solar_insolation[col_order]

    return (wind_speed, solar_insolation)


def write_data(input_parameters, wind_speed, solar_insolation):
    """Write outputs
    """
    # write input parameters to input_parameters table
    input_parameters.to_csv('input_parameters.csv')

    # write the converted data to input_timestep table
    wind_speed.to_csv('wind_speed.csv')
    solar_insolation.to_csv('solar_insolation.csv')
