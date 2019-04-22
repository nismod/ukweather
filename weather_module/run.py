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
