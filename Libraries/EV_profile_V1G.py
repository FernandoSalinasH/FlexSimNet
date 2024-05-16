#%%
## EV charging profiles generator for V1G operation
import numpy as np
import matplotlib.pyplot as plt
import random
import json

def pdf_distance (d, R = 200, sig = 0.92, mu = 3.7): # daily driving distance
    f_dist = (1 / (d * sig * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((np.log(d) - mu) / sig) ** 2)  # daily driving distance
    return f_dist

def pdf_soc (soc, R = 200, sig = 0.92, mu = 3.7): # initial state of charge
    f_soc = (1 / (R * (1 - soc) * sig * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((np.log(R * (1 - soc)) - mu) / sig) ** 2)  # soc = 1-d/R # initial state of charge
    return f_soc

def pdf_time (t, sig = 1, t_med = 17): # start time of charging
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
    f_dist, f_soc, f_t = [], [], []
    for d in daily_usage: 
        f_dist_val = pdf_distance(d)
        f_dist.append(f_dist_val)
    
    for soc in soc_init: 
        f_soc_val = pdf_soc(soc)
        f_soc.append(f_soc_val)

    t_set = np.linspace(0, 24 - 24/1440, 1440) # minutes in a day
    for t in t_set: # minutes in a day
        f_t_val = pdf_time(t)
        f_t_val = 0.0 if np.isnan(f_t_val) else f_t_val
        f_t.append(f_t_val)

    # Normalize Pdfs
    f_dist = np.array(f_dist) / sum(f_dist)
    f_soc = np.array(f_soc) / sum(f_soc)
    f_t = np.array(f_t) / sum(f_t)
    
    # # Plot Pdfs
    # plt.figure()
    # plt.subplot(3, 1, 1)
    # plt.plot(daily_usage, f_dist)
    # plt.title('Daily driving distance')
    # plt.subplot(3, 1, 2)
    # plt.tight_layout()  # Add space between subplots
    # plt.plot(soc_init, f_soc,'red')
    # plt.title('Initial state of charge')
    # plt.subplot(3, 1, 3)
    # plt.plot(t_set, f_t,'green')
    # plt.title('Start time of charging')
    # plt.legend()
    # plt.show()

    # Generate random daily usage based on the provided PDF
    all_profiles = {}
    charging_profile = {}

    for i in range(num_ev):

        # Generate random EV model and charger type
        EV_name = random.choice(EV_model)  # EV model
        EV = EV_model.index(EV_name)
        charger_name = random.choice(chargers)  # charger type
        ch = chargers.index(charger_name)

        soc = np.random.choice(soc_init, size=1, p = f_soc)  # Initial state, e.g., battery charge level
        daily_usage_km = np.random.choice(daily_usage, size=1, p = f_dist) # Generate random daily usage based on the provided PDF
        time_start = np.random.choice(t_set, size=1, p = f_t) # Generate random start time based on the provided PDF

        # Generate random charging duration
        t_charging = (1 - soc)*battery_cap[EV]/chargers[ch] # charging duration
        
        # Update charging profile
        charging_profile = {'EV': EV_name, 'charger_kW': chargers[ch], 'soc': float(soc), 'daily_usage_km': float(daily_usage_km),
                            'time_start': float(time_start), 't_charging': float(t_charging)}

        profile = []
        for t in range(0, 1440):
            if t_set[t] >= time_start and t_set[t] <= time_start + t_charging:
                profile.append(chargers[ch])
            elif t_set[t] < time_start + t_charging - 24:
                profile.append(chargers[ch])
            else:
                profile.append(0)
        
        charging_profile['profile'] =  profile

        all_profiles[i] = charging_profile

    return all_profiles

# Example usage
num_ev = 10

daily_usage = np.linspace(0.00001, 300, 100)  # Adjust based on your actual distribution functions
soc_init = np.linspace(0, 0.99999, 100)

charging_profiles = generate_sequential_charging_profiles(num_ev, daily_usage, soc_init)

# Plotting the sequential charging profiles
t_set = np.linspace(0, 24 - 24/1440, 1440)
for idx, profile in charging_profiles.items():  # Fix the iteration over charging_profiles
    plt.plot(t_set, profile['profile']) # Fix the indexing of idx
plt.xlabel('Time (hours)')
plt.ylabel('Charging load (kW)')
plt.legend()
plt.show()

# with open('EV_charging_profiles_uncontrolled.json', 'w') as f:
#     json.dump(charging_profiles, f)

