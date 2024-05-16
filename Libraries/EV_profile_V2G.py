#%%
## EV charging profiles generator for V2G operation
import numpy as np
import matplotlib.pyplot as plt
import random
import json

def pdf_distance (d, sig = 0.92, mu = 3.7): # daily driving distance
    f_dist = (1 / (d * sig * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((np.log(d) - mu) / sig) ** 2)  # daily driving distance
    return f_dist

def pdf_soc (soc, R, sig = 0.92, mu = 3.7): # initial state of charge
    f_soc = (1 / (R * (1 - soc) * sig * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((np.log(R * (1 - soc)) - mu) / sig) ** 2)  # soc = 1-d/R # initial state of charge
    return f_soc

def pdf_time_char (t, sig = 1, t_med = 0): # start time of charging
    f_t = (1 / ((t - t_med) * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((np.log(t - t_med)) / sig) ** 2)
    return f_t

def pdf_time_dis (t, sig = 1, t_med = 17): # start time of discharging
    f_t = (1 / ((t - t_med) * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((np.log(t - t_med)) / sig) ** 2)
    return f_t

def generate_sequential_charging_profiles(num_ev, daily_usage, soc_init):
    EV_model = ['Tesla Model 3', 'Hyundai Iokiq 6', 'BMW i4 eDrive40', 'BYD ATTO 3', 'Volvo EX30', 'Kia Niro EV', 'Nissan Leaf']
    battery_cap = [75, 74, 80.7, 60.5, 64, 64.8, 39] # kWh 
    automonomy = [505, 440, 515, 330, 365, 385, 235] # km
    effciciency = [0.149, 0.168, 0.157, 0.183, 0.175, 0.168, 0.166] # kWh/km
    fast_charge = [780 , 1150, 800, 370, 540, 390, 230] # km/h
    chargers = [7.4, 7.0, 7.2, 9.6, 11] # kW

    # Generate Pdfs
    f_dist, f_t_c, f_t_d = [], [], []
    for d in daily_usage: 
        f_dist_val = pdf_distance(d)
        f_dist.append(f_dist_val)
    
    # for soc in soc_init: 
    #     f_soc_val = pdf_soc(soc, R)
    #     f_soc.append(f_soc_val)

    t_set = np.linspace(0, 24 - 24/1440, 1440) # minutes in a day
    for t in t_set: # minutes in a day
        f_t_val_c = pdf_time_char(t)
        f_t_val_d = pdf_time_dis(t)
        f_t_val_c = 0.0 if np.isnan(f_t_val_c) else f_t_val_c
        f_t_val_d = 0.0 if np.isnan(f_t_val_d) else f_t_val_d
        f_t_c.append(f_t_val_c)
        f_t_d.append(f_t_val_d)

    # Normalize Pdfs
    f_dist = np.array(f_dist) / sum(f_dist)
    # f_soc = np.array(f_soc) / sum(f_soc)
    f_t_c = np.array(f_t_c) / sum(f_t_c)
    f_t_d = np.array(f_t_d) / sum(f_t_d)
    f_t_c = np.concatenate((f_t_c[2*60:], f_t_c[:2*60])) # reorganize to start at 22h

    # Generate random daily usage based on the provided PDF
    all_profiles = {}
    charging_profile = {}

    for i in range(num_ev):

        # Generate random EV model and charger type
        EV_name = random.choice(EV_model)  # EV model
        EV = EV_model.index(EV_name)
        charger_name = random.choice(chargers)  # charger type
        ch = chargers.index(charger_name)
        R = automonomy[EV] # range

        f_soc = []
        for soc in soc_init: 
            f_soc_val = pdf_soc(soc, R)
            f_soc.append(f_soc_val)
        
        f_soc = np.array(f_soc) / sum(f_soc)

        soc = np.random.choice(soc_init, size=1, p = f_soc)  # Initial state, e.g., battery charge level
        daily_usage_km = np.random.choice(daily_usage, size=1, p = f_dist) # Generate random daily usage based on the provided PDF
        time_start_dis = np.random.choice(t_set, size=1, p = f_t_d) # Generate random start time based on the provided PDF
        time_start_ch = np.random.choice(t_set, size=1, p = f_t_c) # Generate random start time based on the provided PDF
        
        # Generate random charging/discharging duration
        t_discharge = min((soc - 0.2)*battery_cap[EV]/chargers[ch], 22 - time_start_dis) # discharging duration (can discharge until 22h)
        t_charging_max = 7 - time_start_ch if time_start_ch < 7 else 24 - time_start_ch + 7 # can charge until 7am
        t_charging = min((battery_cap[EV] - soc*battery_cap[EV] + chargers[ch]*t_discharge)/chargers[ch], t_charging_max) # charging duration
        
        # Update charging profile
        charging_profile = {'EV': EV_name, 'charger_kW': chargers[ch], 'soc': float(soc), 'daily_usage_km': float(daily_usage_km),
                            'time_start': float(time_start_dis), 't_discharge': float(t_discharge), 't_charging': float(t_charging)}

        profile = []
        for t in range(0, 1440):
            # Discharging
            if t_set[t] >= time_start_dis and t_set[t] <= time_start_dis + t_discharge:
                profile.append(-chargers[ch])
            # Charging
            elif t_set[t] >= time_start_ch and t_set[t] <= time_start_ch + t_charging:
                profile.append(chargers[ch])
            elif t_set[t] < time_start_ch + t_charging - 24:
                profile.append(chargers[ch])
            else:
                profile.append(0)
        
        charging_profile['profile'] =  profile
        # # plt.figure()
        # plt.plot(t_set, profile)
        # plt.show()
        all_profiles[i] = charging_profile
        # Plot Pdfs
    
    plt.figure()
    plt.subplot(4, 1, 1)
    plt.plot(daily_usage, f_dist)
    plt.title('Daily driving distance')
    plt.xlabel('Distance (km)')
    # plt.title('Distance journalière parcourue', fontfamily='Arial', fontsize=14)
    # plt.xlabel('Distance (km)', fontfamily='Arial', fontsize=10)
    plt.ylabel('p(d)', fontfamily='Arial', fontsize=10)
    plt.xlim(0, 100)  # Limit x-axis from 0 to 24
    plt.subplot(4, 1, 2)
    plt.tight_layout()  # Add space between subplots
    plt.plot(soc_init, f_soc,'red')
    plt.title('Initial state of charge')
    plt.xlabel('SOC')
    # plt.title('État de charge initial', fontfamily='Arial', fontsize=14)
    # plt.xlabel('SOC', fontfamily='Arial', fontsize=10)
    plt.ylabel('p(soc)', fontfamily='Arial', fontsize=10)
    plt.xlim(0, 1)  # Limit x-axis from 0 to 24
    plt.subplot(4, 1, 3)
    plt.plot(t_set, f_t_c,'green')
    plt.title('Start time of charging')
    plt.xlabel('Time (hours)')
    # plt.title(r'Heure de début de charge', fontfamily='Arial', fontsize=14)
    # plt.xlabel('Heure', fontfamily='Arial', fontsize=10)
    plt.ylabel('p(h)', fontfamily='Arial', fontsize=10)
    plt.xlim(0, 24)  # Limit x-axis from 0 to 24
    plt.subplot(4, 1, 4)
    plt.tight_layout() 
    plt.plot(t_set, f_t_d,'black')
    plt.title('Start time of discharging')
    plt.xlabel('Time (hours)')
    # plt.title('Heure de début de décharge', fontfamily='Arial', fontsize=14)
    # plt.xlabel('Heure', fontfamily='Arial', fontsize=10)
    plt.ylabel('p(h)', fontfamily='Arial', fontsize=10)
    plt.xlim(0, 24)  # Limit x-axis from 0 to 24
    plt.show()
    
    return all_profiles
    
# Example usage
num_ev = 1000

daily_usage = np.linspace(0.00001, 100, 100)  # Adjust based on your actual distribution functions
soc_init = np.linspace(0, 0.99999, 100)

charging_profiles = generate_sequential_charging_profiles(num_ev, daily_usage, soc_init)

t_set = np.linspace(0, 24 - 24/1440, 1440)
# Plotting the sequential charging profiles
plt.figure()
plt.subplot(2, 1, 1)
for idx, profile in charging_profiles.items():  # Fix the iteration over charging_profiles
    plt.plot(t_set, profile['profile']) # Fix the indexing of idx
# plt.xlabel('Time (hours)')
# plt.ylabel('EVs load (kW)')
plt.ylabel('Charge des VE (kW)', fontfamily='DejaVu Sans', fontsize=12)
plt.xticks(np.arange(0, 25, 1))  # Set the x-axis ticks to show all 24 hours
plt.xlim(0, 24)
# plt.show()

# Initialize a list of zeros with the same length as a profile
total_profile = [0] * len(charging_profiles[0]['profile'])

# Sum all the profiles
for idx, profile in charging_profiles.items():
    total_profile = [sum(x) for x in zip(total_profile, profile['profile'])]

plt.subplot(2, 1, 2)
# Plot the total profile as a filled curve in green
plt.fill_between(t_set, total_profile, color="green", alpha=0.5)
plt.plot(t_set, total_profile, color="green", alpha=1, linewidth=1)
# plt.xlabel('Time (hours)')
# plt.ylabel('EVs aggregated load (kW)')
plt.xlabel('Heure', fontfamily='DejaVu Sans', fontsize=12)
plt.ylabel('Charge agrégée des VE (kW)', fontfamily='DejaVu Sans', fontsize=12)
plt.xticks(np.arange(0, 25, 1))  # Set the x-axis ticks to show all 24 hours
plt.xlim(0, 24) 
plt.show()

# with open(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Network_data\EV_charging_profiles.json", 'w') as f:
#     json.dump(charging_profiles, f)
