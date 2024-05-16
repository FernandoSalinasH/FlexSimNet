#%% Home Energy Modelling 
# Running E+ in parallel> residential examples
# Prepared by: Fernando Salinas-Herrera

import os
import time
from eppy.modeleditor import IDF
from eppy.runner.run_functions import runIDFs
import esoreader
import pandas as pd
import numpy as np
import multiprocessing
import json
from Libraries.LoggingUtil import LoggingUtil
# from LoggingUtil import LoggingUtil

q_listener, q , logging = LoggingUtil.logger_init(__name__)

class Building_EM:
    
    def __init__(self):
        logging.info(f"\033[1mStarting building energy modelling tool\033[0m")
        iddfile = "C:\EnergyPlusV9-6-0\Energy+.idd"
        IDF.setiddname(iddfile)
        self.main_path = os.path.dirname(os.path.realpath(__file__))
        self.epwfile = os.path.join(self.main_path,"..","Weather_data","Quebec_city.epw")
    
    def make_eplaunch(self, idf):
        """Make options for run, so that it runs like EPLaunch on Windows"""
        idfversion = idf.idfobjects["version"][0].Version_Identifier.split(".")
        idfversion.extend([0] * (3 - len(idfversion)))
        idfversionstr = "-".join([str(item) for item in idfversion])
        fname = idf.idfname
        options = {"ep_version": idfversionstr,  # runIDFs needs the version number
            "output_prefix": os.path.basename(fname).split(".")[0],
            "output_suffix": "C",
            "output_directory": os.path.dirname(fname),
            "readvars": True,
            "expandobjects": True,}
        return options
   
    def time_control(self, idf_mod):
        # Controlling time parameters for simulation
        idf_mod.idfobjects["Timestep"][0].Number_of_Timesteps_per_Hour = self.time_step
        idf_mod.idfobjects["RunPeriod"][0].Begin_Month = self.month_from
        idf_mod.idfobjects["RunPeriod"][0].Begin_Day_of_Month = self.day_from
        idf_mod.idfobjects["RunPeriod"][0].End_Month = self.month_to
        idf_mod.idfobjects["RunPeriod"][0].End_Day_of_Month = self.day_to

    def temperature_control(self, idf_mod):
        # Controlling thermostat temperature for residential costumers
        idf_mod.idfobjects["Schedule:Compact"][15].Field_3 = 'Until: 17:00'
        idf_mod.idfobjects["Schedule:Compact"][15].Field_4 = self.temp_normal # degrees Celsius
        idf_mod.idfobjects["Schedule:Compact"][15].Field_5 = 'Until: 22:00'
        idf_mod.idfobjects["Schedule:Compact"][15].Field_6 = self.temp_comfort # degrees Celsius
        idf_mod.idfobjects["Schedule:Compact"][15].Field_7 = 'Until: 24:00'
        idf_mod.idfobjects["Schedule:Compact"][15].Field_8 = self.temp_normal # degrees Celsius

    def get_results(self):
        # Reading results from eso files to dictionaries
        JtokWh = 1 / 36e5  # Conversion Joules to kWh
        to_kW = self.time_step # convert to kWh to kW
        time_set = np.arange(60/self.time_step, (self.day_to - self.day_from + 1) * 24 * 60 + 60/self.time_step, 60/self.time_step).tolist()

        total_house_kW = [8.82624,11.85542,10.55842,8.89021,1.81924,2.29425,1.84707,1.79906,7.46215,8.82572,8.73706,7.63743,2.66997,3.07447,2.70765,
            2.6605,59.38012,85.06301,70.7357,58.55322,20.10774,20.06156,19.70307,19.29214,53.79763,71.32102,60.52218,52.99604,33.97589,
                35.69278,34.38945,33.94411] # Values got from houses design
        
        # Creating dictionaries for results
        results = {'kW': {}, 'electricity': {}, 'heating': {}, 'cooling': {}, 'tempout': {}, 'tempin': {}, 'heatgas': {}}

        for i in range(self.idf_from, self.idf_to + 1):
            eso_path = os.path.join(self.main_path, "..", "idf_residential", f'idf_{i}.eso')  # Getting path for eso files
            eso = esoreader.read_from_path(eso_path)  # Reads eso files
            
            # Extracting results and storing in dictionaries
            results['kW'][i] = total_house_kW[ i - 1]
            results['electricity'][i] = (eso.to_frame('Electricity:Facility', index=time_set) * JtokWh * to_kW).values.tolist()
            results['heating'][i] = (eso.to_frame('Heating:Electricity', index=time_set) * JtokWh * to_kW).values.tolist()
            results['cooling'][i] = (eso.to_frame('Cooling:Electricity', index=time_set) * JtokWh * to_kW).values.tolist()
            results['tempout'][i] = eso.to_frame('Site Outdoor Air Drybulb Temperature', index=time_set).values.tolist()
            results['tempin'][i] = eso.to_frame('Zone Mean Air Temperature', index=time_set).values.tolist()
            # if len(eso.to_frame('Heating:NaturalGas')) != 0:
            results['heatgas'][i] = (eso.to_frame('Heating:NaturalGas', index=time_set) * JtokWh * to_kW).values.tolist()
        self.results = results

    def build_simulation(self):
        self.fnames = []
        # Reading idf files and building simulation and parameters
        for i in range(self.idf_from, self.idf_to + 1):
            # Define path for idf diles
            idf = os.path.join(self.main_path,"..","idf_residential",'idf_'+ str(i) + r".idf")
            idf_mod = IDF(idf)
            self.time_control(idf_mod)
            self.temperature_control(idf_mod)
            idf_mod.save()
            self.fnames.append(idf)
    
    def run_parallel(self, idf_from, idf_to, time_step, month_from, month_to, day_from, day_to, temp_normal, temp_comfort):
        # Function to run in parallel Energy+
        time_total_start = time.time()
        # Define time parameters for simulation
        self.time_step = 60/time_step  # minutes step/hour
        self.day_from = day_from # day from
        self.month_from = month_from # month from
        self.day_to = day_to # day to
        self.month_to = month_to # month to
        self.temp_normal = temp_normal
        self.temp_comfort = temp_comfort

        # Define buildings to simulate
        self.idf_from = idf_from
        self.idf_to = idf_to

        time_build_start = time.time()
        self.build_simulation()
        time_build_finish = time.time()
        logging.info(f'Time to build simulation for {self.idf_to - self.idf_from + 1} building = {time_build_finish - time_build_start:.3f} seconds')

        # Parallel simulation using eppy
        time_run_start = time.time()
        idfs = (IDF(fname, self.epwfile) for fname in self.fnames)
        runs = ((idf, self.make_eplaunch(idf)) for idf in idfs)
        num_CPUs = multiprocessing.cpu_count()  # number of cores to run in parallel
        runIDFs(runs, num_CPUs - 1)
        time_run_finish = time.time()
        logging.info(f"Time to simulate {(self.day_to - self.day_from + 1)*24} hours = {time_run_finish - time_run_start:.3f} seconds")
        
        time_res_start = time.time()
        self.get_results()
        time_res_finish = time.time()
        logging.info(f"Time to get results = {time_res_finish - time_res_start:.3f} seconds ")
        time_total_finish = time.time()
        logging.info(f'\033[1mTotal time for bulding_EM tool= {time_total_finish - time_total_start:.3f} seconds')
        # logging.info("Finished!")
        return self.results

if __name__ == "__main__":
    idf_from = 1 # idf file to start
    idf_to = 2  # idf file to finish, max 32
    time_step = 5  # min
    month_from = 1 # month from
    month_to = 1 # month to
    day_from = 12 # day from
    day_to = 12 # day to
    temp_normal = 22 # Celsius
    temp_comfort = 18 # Celsius
    Building_EM = Building_EM()
    results = Building_EM.run_parallel(idf_from, idf_to, time_step, month_from, month_to, day_from, day_to, temp_normal, temp_comfort)
    # results['electricity'] options: 'kW' 'heating' 'cooling' 'tempout' 'tempin'
    
    with open(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Network_data\Home_Energy_Models_"+ str(temp_comfort) +"_Celsius.json", 'w') as f:
        json.dump(results, f)
        

# %%
