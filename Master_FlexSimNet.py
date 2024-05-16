#%% FlexSimNet: Master file 
# Created by: Fernando Salinas-Herrera
# Faculté des sciences et génie
# Département de génie électrique et de génie informatique
# Université Laval
# Doctorat en génie électrique
  
from Libraries.GTSPF import GenericPowerFlow
from Libraries.Building_EM import Building_EM
import multiprocessing
from datetime import datetime
import time
import json
import pandas as pd
from Libraries.LoggingUtil import LoggingUtil
import matplotlib.pyplot as plt

### Simulation settings ###

# Setting for power flow
Network_ids = ['IEEE13'] # options: 'IEEE13' 'IEEE123' 'IEEE8500' 'IEEE9500' 'GSO_feeder_0'
simulation_time = 24  # hours
time_step_pf = 60  # minutes
EV_penetration = 0.3 # from 0 to 1
PV_penetration = 0.3 # from 0 to 1
Storage_penetration = 0.2 # from 0 to 1

# Settings for hourse energy model
idf_from = 1 # idf file to start
idf_to = 32  # idf file to finish, max 32
time_step_em = time_step_pf  # minutes
year = 2022
start_month = 1 # month from
end_month = 1 # month to
start_day = 12 # day from
end_day = 12 # day to
temp_normal = 22 # Celsius
temp_comfort = 22 # Celsius

def GTSPF_run_simulation(network, results_EM):
    # Function to make run_simulation iterable
    GTSPF = GenericPowerFlow()
    GTSPF.setup_networks(network)
    GTSPF.setloadprofiles(network, results_EM)
    GTSPF.EV_load(EV_penetration)
    GTSPF.PV_systems(PV_penetration)
    GTSPF.Storage_systems(Storage_penetration)
    results, info_network = GTSPF.runpowerflow(network, simulation_time, time_step_pf)
    return results, info_network
    

if __name__ == '__main__':
    # Set logging for multiprocessing 
    q_listener, q , logging = LoggingUtil.logger_init(__name__)
    worker_init = LoggingUtil.worker_init

    # Building_EM simulation
    if 1 == 1:
        building_EM = Building_EM()
        results_EM = building_EM.run_parallel(idf_from, idf_to, time_step_em, start_month, end_month, start_day, end_day, temp_normal, temp_comfort)
    else:
        with open(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Network_data\Home_Energy_Models_22_Celsius.json", 'r') as f:
            results_EM = json.load(f)

    # Multiprocessing simulation
    logging.info(f'\033[1mStarting GTSPF tool to simulate networks: {Network_ids}\033[0m')
    time_start = time.time()
    processes=multiprocessing.cpu_count()
    with multiprocessing.Pool(processes,worker_init, [q]) as pool:
        results = {}
        info_network = {}
        for network, (result, info_network) in zip(Network_ids, pool.starmap(GTSPF_run_simulation, [(network, results_EM) for network in Network_ids])):
            results[network] = result
            print(info_network)
    q_listener.stop()
    time_finish = time.time()
    logging.info(f"\n\033[1mTotal time to simulate networks {Network_ids} for time = {simulation_time} hours, step = {time_step_pf} minutes is {time_finish - time_start:.3f} seconds")
    logging.info("Finished!")
    # results['network']['Voltage'] options: 'Voltage','S_power','P_power','Q_power','I_mag','P_Losses','Q_Losses')
    
    # # Save results in excel files
    # options = ['Voltage','S_power','P_power','Q_power','I_mag','P_Losses','Q_Losses','Line_loading','Tra_loading']
    # with pd.ExcelWriter(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\prueba.xlsx", engine='xlsxwriter') as writer:
    #     for i in options:
    #         results[Network_ids[0]][i].to_excel(writer, sheet_name = i)

    # %%
    data = results['IEEE13']['Voltage'].values.flatten()
    plt.hist(data, bins=30, edgecolor='black')
    plt.show()

    #%%
    data = results['IEEE13']['P_power']
    data = data.T
    data.plot(kind='line', legend=False)
    plt.show