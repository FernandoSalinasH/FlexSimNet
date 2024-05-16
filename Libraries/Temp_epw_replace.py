#%%
import pandas as pd
import pandas as pd

# Define the column names (based on the EPW file format)
column_names = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Data Source and Uncertainty Flags',
                'Dry Bulb Temperature', 'Dew Point Temperature', 'Relative Humidity',
                'Atmospheric Station Pressure', 'Extraterrestrial Horizontal Radiation',
                'Extraterrestrial Direct Normal Radiation', 'Horizontal Infrared Radiation Intensity',
                'Global Horizontal Radiation', 'Direct Normal Radiation', 'Diffuse Horizontal Radiation',
                'Global Horizontal Illuminance', 'Direct Normal Illuminance', 'Diffuse Horizontal Illuminance',
                'Zenith Luminance', 'Wind Direction', 'Wind Speed', 'Total Sky Cover', 'Opaque Sky Cover (used if Horizontal IR Intensity missing)',
                'Visibility', 'Ceiling Height', 'Present Weather Observation', 'Present Weather Codes',
                'Precipitable Water', 'Aerosol Optical Depth', 'Snow Depth', 'Days Since Last Snowfall',
                'Albedo', 'Liquid Precipitation Depth', 'Liquid Precipitation Quantity']

# Read the EPW file
# Skip the first 8 rows because they contain metadata, not actual weather data
df = pd.read_csv(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Weather_data\Originals\CAN_QC_Quebec.City-Ste.Foy-Univ.Laval.713920_TDY-CWEC2020v2.epw", skiprows=8, header=None, names=column_names)

# Replace the 'Dry Bulb Temperature' column with your new data
# Replace 'your_new_data' with your actual data
data = pd.read_csv(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\temp_irradiance.csv")
your_new_data = data['temperature'].values[:8760]
df['Dry Bulb Temperature'] = your_new_data

# Write the DataFrame back to an EPW file
df.to_csv(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Weather_data\Quebec_city_2020.epw", index=False, header=False)

#%%
import pandas as pd

# Define the column names (based on the EPW file format)
column_names = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'Data Source and Uncertainty Flags',
                'Dry Bulb Temperature', 'Dew Point Temperature', 'Relative Humidity',
                'Atmospheric Station Pressure', 'Extraterrestrial Horizontal Radiation',
                'Extraterrestrial Direct Normal Radiation', 'Horizontal Infrared Radiation Intensity',
                'Global Horizontal Radiation', 'Direct Normal Radiation', 'Diffuse Horizontal Radiation',
                'Global Horizontal Illuminance', 'Direct Normal Illuminance', 'Diffuse Horizontal Illuminance',
                'Zenith Luminance', 'Wind Direction', 'Wind Speed', 'Total Sky Cover', 'Opaque Sky Cover (used if Horizontal IR Intensity missing)',
                'Visibility', 'Ceiling Height', 'Present Weather Observation', 'Present Weather Codes',
                'Precipitable Water', 'Aerosol Optical Depth', 'Snow Depth', 'Days Since Last Snowfall',
                'Albedo', 'Liquid Precipitation Depth', 'Liquid Precipitation Quantity']

epw_file = r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Weather_data\Originals\CAN_QC_Quebec.City-Ste.Foy-Univ.Laval.713920_TDY-CWEC2020v2.epw"
# Read the header lines from the EPW file
with open(epw_file, 'r') as f:
    header_lines = [next(f) for _ in range(8)]

# Read the EPW file
df = pd.read_csv(epw_file, skiprows=8, header=None, names=column_names)

# Replace the 'Dry Bulb Temperature' column with your new data
data = pd.read_csv(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\temp_irradiance.csv")
your_new_data = data['temperature'].values[:8760]
df['Dry Bulb Temperature'] = your_new_data

# Write the header lines and the DataFrame back to a new EPW file
new_epw = r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Weather_data\Quebec_city.epw"
with open(new_epw, 'w') as f:
    for line in header_lines:
        f.write(line)
    df.to_csv(f, index=False, header=False)