#%% GTSPF: Generic Time Series Power Flow
# version 3: include losses from monitors, problems with extracting from Monitors, may need to change strategy,
# version 4: delete monitors as too many monitors for 8500 node gets a bug and magnitudes remain constant. Hence, we 
# use dssText.Command = "Set number = " to do a loop and get voltage from AllBusVoltages function
# version 7: this version runs parallel processing using OpenDSSA multiprocessing built-in option. 
#            But, it does not parallelize the extraction of results which is more time comsuming (next version will use 
#            Python parallelization option to include results) 
# version 8: version to run parallel processing using Python option. Aims to parallelize power flow and resuls processing
# version 9: includes load profiles from Energy+
"""
Generic Time series power flow (GTSPF)
Author = Fernando Salinas-Herrera
"""
import os
import sys
import numpy as np
import pandas as pd
import time
import math
import json
import win32com.client
from win32com.client import makepy
from Libraries.LoggingUtil import LoggingUtil

q_listener, q , logging = LoggingUtil.logger_init(__name__)

class GenericPowerFlow:
    
    def __init__(self):
        ## Create new instance of OpenDSS
        # Early biding configuration for OpenDSSS
        sys.argv = ["makepy", "OpenDSSEngine.DSS"]
        makepy.main()
        self.dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")

        self.dssObj.ClearAll()
        # Set OpenDSS engine (assign variables to interfaces for easy access)
        self._dss_circuit = self.dssObj.ActiveCircuit
        self.dssObj.AllowForms = False
        self._dss_element = self._dss_circuit.ActiveCktElement
        self._dss_text = self.dssObj.Text
        self._class = self._dss_circuit.ActiveClass
        self._dss_solution = self._dss_circuit.Solution
        self._dss_loads = self._dss_circuit.Loads
        self._dss_PV = self._dss_circuit.PVSystems
        self._dss_lines = self._dss_circuit.Lines
        self._dss_trafo = self._dss_circuit.Transformers
        self._dss_bus = self._dss_circuit.ActiveBus
        self._dss_reduce_ckt = self._dss_circuit.ReduceCkt
        self._dss_parallel = self._dss_circuit.Parallel
        self.dssObj.ClearAll()  # clear any existing circuit in the engine

    def compileDSS(self, dssFile, network_id):
        ## Compile OpenDSS
        compile_start_time = time.time()
        logging.info(f"Compiling DSS network {network_id}.")
        self._dss_text.Command = "Compile " + dssFile
        compile_end_time = time.time()
        logging.info(f"Time to compile network {network_id}: {compile_end_time - compile_start_time:.3f} seconds")
    
    def network_info(self, network_id):
        # Get network information 
        # network_id = self._dss_circuit
        Lines = self._dss_lines.Count
        Nodes = self._dss_circuit.NumNodes
        Loads = self._dss_loads.Count
        try:
            EVs = self.num_ev
        except AttributeError:
            EVs = 0
        PV = self._dss_PV.Count
        self._dss_circuit.SetActiveClass("storage")
        Storage = self._class.Count
        info_network = (f"\n\033[1mNetwork information for {network_id}:\033[0m \n Lines = {Lines} \
                      \n Loads = {Loads} \n Nodes = {Nodes} \n EVs = {EVs} \n PV = {PV} \n Storage = {Storage} \n\n")
        return info_network
    
    def setloadprofiles(self, network_id, results_EM):
        ## Setting load profiles
        logging.info(f"\033[1mCoordinating results from building_EM and loads in GTSPF for {network_id}...\033[0m")

        kW_profiles = results_EM['electricity'] # get all consumption profiles 
        houses_keys = list(results_EM['kW'].keys()) 
        houses_kW = list(results_EM['kW'].values()) #  get nominal kW of each house
        self.original_count_loads = self._dss_loads.Count
        self.original_loads_names = self._dss_loads.AllNames
        self.original_loads_kVA = {}
        self.original_loads_kW = {}
        for i, load in zip(range(self.original_count_loads), self.original_loads_names):
            self._dss_loads.Name = load
            load_kW = self._dss_loads.kW
            load_pf = self._dss_loads.PF
            kVA_load = self._dss_loads.kva
            house_id_aux = min(range(len(houses_kW)), key=lambda i: abs(houses_kW[i] - load_kW)) # Find the most similar kW in the house pool
            house_id = houses_keys[house_id_aux]
            Loadshape_P = (np.array(kW_profiles[house_id])).flatten()
            Loadshape_Q = Loadshape_P* math.tan(math.acos(load_pf))
            Loadshape_P = ' '.join(str(number) for number in Loadshape_P)
            Loadshape_Q = ' '.join(str(number) for number in Loadshape_Q)
            npts = int(len(kW_profiles[house_id]))
            mininterval = int((60*24)/len(kW_profiles[house_id]))
            self._dss_text.Command = (
                "New Loadshape.Shape_" + str(i + 1) + 
                " npts=" + str(npts) + " minterval = " + str(mininterval) +
                " pmult=(" + Loadshape_P + ")" +
                " qmult=(" + Loadshape_Q + ")" + 
                " useactual=true"
            ) # when false uses profiles as multipliers, when true uses profiles as actual values and ignores fixed load powers
            self.original_loads_kVA[load] = kVA_load
            self.original_loads_kW[load] = load_kW
            self._dss_loads.daily = "Shape_" + str(i + 1)

    def save_network(self,name):
        ## Function to save modified circuit
        self._dss_reduce_ckt.SaveCircuit(name)

    def set_dataframes_results(self,simulation_time, time_step):
        ## Function to define dataframes for results
        self.Time_set = np.arange(time_step, simulation_time * 60 + time_step, time_step)  # Time set for simulations
        self.Node_set = self._dss_circuit.AllNodeNames
        self.Elements = self._dss_circuit.AllElementNames
        self.Bus_Voltage = pd.DataFrame(data=0, index=self.Node_set,columns=self.Time_set) # Node voltages in pu
        self.P_Losses = pd.DataFrame(data=0, index=self.Elements, columns=self.Time_set).rename_axis('Element') # Active losses in kW
        self.Q_Losses = pd.DataFrame(data=0, index=self.Elements, columns=self.Time_set).rename_axis('Element') # Reactive losses in kVAr
        self.P_power = pd.DataFrame(index=pd.MultiIndex(levels=[[], []], codes=[[], []], names=['Element', 'Bus']), columns=self.Time_set) # Active power in kW
        self.Q_power = pd.DataFrame(index=pd.MultiIndex(levels=[[], []], codes=[[], []],names=['Element', 'Bus']), columns=self.Time_set) # Reactive power in kVAr
        self.I_mag = pd.DataFrame(index=pd.MultiIndex(levels=[[], [], [], []], codes=[[], [], [], []], names=['Element', 'Bus1', 'Bus2', 'Phase']), columns=self.Time_set)  # Current magnitude in Amp
        self.S_power = pd.DataFrame(index=pd.MultiIndex(levels=[[], []], codes=[[], []], names=['Element', 'Bus']), columns=self.Time_set)  # 3 phase apparent power at each terminal in kVA
    
    def get_results(self,time_tag):
        ## Function to get power flow results
        # Get voltages for each node in pu
        self.Bus_Voltage[time_tag] = self._dss_circuit.AllBusVmagPu
        # Get active and reactive losses for each element in kW and KVAr
        self.P_Losses[time_tag] = self._dss_circuit.AllElementLosses[::2]
        self.Q_Losses[time_tag] = self._dss_circuit.AllElementLosses[1::2]
        A = self._dss_circuit.TotalPower
        B = self._dss_circuit.Losses
        # Get line currents in Amperes 
        for line in  self._dss_lines.AllNames:
            self._dss_lines.Name = line
            currents = self._dss_element.CurrentsMagAng # get currents mag in Amp and angle in degrees
            Bus_1 = self._dss_lines.Bus1.split(".")[0]
            Bus_2 = self._dss_lines.Bus2.split(".")[0]
            phases = self._dss_lines.Phases
            for phase in range(phases):
                self.I_mag.loc[(line,Bus_1,Bus_2,phase + 1),time_tag] = currents[phase * 2]
        # Get apparent, active and reactive powers for each element in KVA, kW and KVAr
        for elem in self.Elements:
            self._dss_circuit.SetActiveElement(elem)
            # if self._dss_element.Enabled is True:
            currents = self._dss_element.CurrentsMagAng # get currents mag in Amp and angle in degrees
            total_powers = self._dss_element.TotalPowers # get Total power in kVA
            C = self._dss_element.Losses 
            buses = self._dss_element.BusNames
            for bus, j in zip(buses , range(len(buses))):
                self.P_power.loc[(elem, bus),time_tag] = total_powers[j*2]
                self.Q_power.loc[(elem, bus),time_tag] = total_powers[j*2+1]
                self.S_power.loc[(elem, bus),time_tag] = np.sqrt((total_powers[j*2])**2 + (total_powers[j*2+1])**2)

    def network_evaluation(self):
        ## Function to perform network evaluation
        logging.info('Getting loading capacity for lines and transformers.')
        # Get line loading capacity
        self.Line_loading = pd.DataFrame() # lines loading
        for line in self._dss_lines.AllNames:
            self._dss_lines.Name = line
            # if self._dss_element.Enabled is True:
            normI = self._dss_lines.NormAmps/self._dss_lines.Phases
            I_line = self.I_mag.loc[(line, slice(None)), :]
            I_line = I_line / normI
            self.Line_loading = pd.concat([self.Line_loading,I_line])
        # Get transformers loading capacity
        self.Trafo_loading = pd.DataFrame()  # transformer loading
        trafos_name = self._dss_trafo.AllNames
        for trafo in trafos_name:
            # if  self._dss_element.Enabled:
            self._dss_trafo.Name = trafo
            normkVA = self._dss_trafo.kva
            S_trafo = self.S_power.loc[('Transformer.'+trafo, slice(None)), :]
            S_trafo = S_trafo / normkVA
            self.Trafo_loading = pd.concat([self.Trafo_loading, S_trafo])
        return [self.Line_loading, self.Trafo_loading]

    def PV_systems(self, penetration):
        ## Function to manage PV systems
        # Distributes PV systems uniformely to loads according to given penetration
        self.penetration = penetration
        if self.penetration > 0:
            # logging.info(f"Deploying PV systems...")
            PV_start_time = time.time()
            # Select loads to deploy PVs by penetration
            Loads_count = self.original_count_loads
            Loads_names = self.original_loads_names
            step = 1//penetration
            if step == 1: # if can't pick distributed elements, gets the first n-elements 
                self.Loads_selected = Loads_names[:int(Loads_count*penetration)]
            else:
                self.Loads_selected = Loads_names[:Loads_count:int(step)]

            # Deploy PV system at each selected 
            for load in self.Loads_selected:
                # Create irradiance shape
                with open(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Weather_data\GHI_LSTM_prediction.json", 'r') as f:
                    GHI_profile = json.load(f)[744+(15*24):744+(16*24)] # 15 January is the day of the simulation 
                max_GHI = max(GHI_profile) # in W/m2
                GHI_shape = [x / max_GHI for x in GHI_profile]
                GHI_shape = (np.array(GHI_shape)).flatten()
                GHI_shape = ' '.join(str(number) for number in GHI_shape)
                self._dss_text.Command = (
                    "New LoadShape.MyGHI"  +
                    " npts = 24 interval = 1 " + # hourly profile for 31 days
                    " mult= (" + GHI_shape + ")" )
                self._dss_loads.Name = load
                kV_load = self._dss_loads.kV
                kVA_load = self.original_loads_kVA[load]
                bus = self._dss_element.Properties('bus1').Val
                PV_name = 'PV_' + self._dss_loads.Name
                self._dss_text.Command = (
                    "New PVSystem." + PV_name
                    + " bus1 = " + str(bus)
                    + " phases = 1"
                    + " kV = " + str(kV_load) 
                    + " kVA = " + str(kVA_load*1)
                    + " Pmpp = " + str(kVA_load*1.1)
                    + " %Cutout = 0.1"
                    + " %Cutin = 0.1"
                    # + " Model = 1"
                    + " pf = 1.0"
                    + " irradiance = " + str(max_GHI/100) # to be in kW/m2
                    + " daily = MyGHI")
            PV_end_time = time.time()
            logging.info(f"Time to deploy PV systems = {PV_end_time - PV_start_time:.3f} seconds")
    
    def Storage_systems(self, penetration):
        # Function to manage Storage systems
        # Distributes Storage systems where PV are
        self.penetration = penetration
        if self.penetration > 0:
            # logging.info(f"Deploying Storage systems at PV buses.")
            Storage_start_time = time.time()
            # Set price profile for network
            Price_shape = open(self.price_shape).read().replace("\n", " ")
            self._dss_text.Command = (
                    "New PriceShape.Price npts=1440 minterval=1 "
                    + "price = [" + Price_shape + "]")
            self._dss_text.Command = "Set pricecurve = Price"
            # Deploy storage systems
            for load in self.Loads_selected:
                self._dss_loads.Name = load
                kV_load = self._dss_loads.kV
                kW_load = self.original_loads_kW[load]
                bus = self._dss_element.Properties('bus1').Val
                Storage_name = 'Storage_' + self._dss_loads.Name
                self._dss_text.Command = (
                    "New Storage." + Storage_name
                    + " bus1 = " + str(bus)
                    + " phases = 1"
                    + " kV = " + str(kV_load) 
                    + " kWrated = " + str(kW_load) # Set inverter kW value 
                    + " kWhrated = " + str(kW_load*4) # assume a supply for 4 hours 
                    + " %reserve = 20" # % in reserve for normal operation
                    + " %stored = 40" # Initial % of stored capacity
                    + " state = idling" # initial state 
                    + " dispmode = price"
                    + " Model = 1" # Storage element injects/absorbs a CONSTANT power.
                    + " pf = 1.0"
                    + " dischargeTrigger = 65" # price to discharge battery
                    + " chargeTrigger = 50") #price to charge battery
            Storage_end_time = time.time()
            logging.info(f"Time to deploy Storage systems = {Storage_end_time - Storage_start_time:.3f} seconds")

    def EV_load(self, penetration):
        # Gets EV profiles resulting from EV_prifle_V2G
        with open(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Network_data\EV_charging_profiles.json", 'r') as f:
            EV_profiles = json.load(f)
        # Distributes EVs uniformely to loads according to given penetration
        self.penetration = penetration
        if self.penetration > 0:
            # logging.info(f"Deploying EVs...")
            PV_start_time = time.time()
            # Select buses to deploy EVs
            buses = [] # Get buses with loads
            for load in self._dss_loads.AllNames:
                self._dss_loads.Name = load
                bus = (self._dss_element.Properties('bus1').Val).split('.')[0]
                buses.append(bus)
            buses = list(dict.fromkeys(buses))
            step = 1//penetration
            if step == 1: # if it can't pick distributed elements, gets the first n-elements 
                buses_selected = buses[:int(len(buses)*penetration)]
            else:
                buses_selected = buses[:len(buses):int(step)] 

            # Deploy PV system at each selected load
            self.num_ev = len(buses_selected)
            for i in range(self.num_ev):
                # Create EV shapes
                EV_shape_name = "EV_shape_" + str(i)
                EV_shape = (np.array(EV_profiles[str(i)]['profile'])).flatten()
                EV_shape = ' '.join(str(number) for number in EV_shape)
                self._dss_text.Command = (
                "New LoadShape." + EV_shape_name +
                " npts=1440 minterval=1" + 
                " pmult= (" + EV_shape + ")" +
                " useactual=true")
                # when false uses profiles as multipliers, when true uses profiles as actual values and ignores fixed load powers)    

                # Create load
                bus = buses_selected[i]
                self._dss_circuit.SetActiveBus(bus)
                phases = self._dss_bus.NumNodes
                nodes = self._dss_bus.Nodes
                nodes = ".".join(str(number) for number in nodes)
                kV_load = (self._dss_bus.kVBase)*math.sqrt(3) if int(phases) > 1 else self._dss_bus.kVBase
                EV_name = 'EV_' + str(i) + "_" + str(bus)
                self._dss_text.Command = (
                    " New Load." + str(EV_name)
                    + " phases = " + str(phases)
                    + " Bus1 = " + str(bus) + '.' + nodes
                    + " kv = " + str(kV_load) 
                    + " status = variable"
                    + " model = 1"
                    + " conn = wye"
                    + " kW = 1.0"
                    + " pf = 1.0"
                    + " Vminpu = 0.88"
                    + " daily = (" + "EV_shape_" + str(i) + ")")
            PV_end_time = time.time()
            logging.info(f"Time to deploy PV systems = {PV_end_time - PV_start_time:.3f} seconds")

    def setup_networks(self, network_id):
        self.price_shape = r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Network_data\13bus\Load_profiles\Price_profile.txt" # Price shape
        # Redirecting available networks:
        main_path = os.path.dirname(os.path.realpath(__file__))
        if network_id == 'IEEE13':
            path_dss_file = os.path.join(main_path,"..","Network_data","13bus","IEEE13Nodeckt.dss")
            self.compileDSS(path_dss_file,network_id)
        elif network_id == "IEEE123":
            path_dss_file = os.path.join(main_path, "..", "Network_data","123Bus","IEEE123Master.dss")
            self.compileDSS(path_dss_file,network_id)
        elif network_id == "IEEE8500":
            path_dss_file = os.path.join(main_path,'..',"Network_data","8500-Node","Master-unbal.dss")
            self.compileDSS(path_dss_file,network_id)
        elif network_id == "IEEE9500":
            path_dss_file = os.path.join(main_path,"..","Network_data","ieee9500","Master-unbal-initial-config.dss")
            self.compileDSS(path_dss_file,network_id)
        elif network_id == "Greensboro": # Loadshapes already defined in dss, 1 year loadshapes, 15 min resolution
            path_dss_file = os.path.join(main_path,"..","Network_data","enter path")
            self.compileDSS(path_dss_file,network_id)
        elif network_id == "GSO_feeder_0": # Loadshapes already defined in dss, 1 year loadshapes, 15 min resolution
            path_dss_file = os.path.join(main_path,"..","Network_data","Greensboro_GSO_urban_SH_BH_1_day","uhs0_1247","uhs0_1247--udt12274","Master.dss")
            self.compileDSS(path_dss_file,network_id)
        else:
            logging.error("Unknown feeder")

    def runpowerflow(self, network_id, simulation_time, time_step):
        ## Function to perfom time series power flow

        # Set up network (compiliation, load profiles, PV, storage)
        # self.setup_networks(network_id)

        # Display network information
        info_network = self.network_info(network_id)

        # Simulation parameters
        self._dss_text.Command = "Set Mode = Daily" # Yearly, Daily
        self._dss_text.Command = "Set stepsize = " + str(time_step) + "m"
        original_steps = int(simulation_time * 60 / time_step)
        self._dss_solution.MaxIterations = 20
        self._dss_solution.Number = 1

        # Create dataframes for results
        self.set_dataframes_results(simulation_time, time_step)

        logging.info(f"\033[1mExecuting power flow for {network_id}...\033[0m")
        # Run power flow step by step
        for steps in range(original_steps):
            pf_start_time = time.time()
            time_tag =  (steps + 1)*time_step
            self._dss_solution.Solve()
            pf_end_time = time.time()
            logging.info(f"Time to compute power flow for {network_id} for step {time_tag} min = {pf_end_time - pf_start_time:.3f} seconds")
            results_start_time = time.time()
            self.get_results(time_tag)
            results_end_time = time.time()
            logging.info(f"Time to get results for {network_id} for step {time_tag} min = {results_end_time - results_start_time:.3f}")
        
        self.network_evaluation()
        # Storing all results in a dictionary
        self.results = {'Voltage':self.Bus_Voltage,'S_power':self.S_power,'P_power':self.P_power,
                        'Q_power': self.Q_power,'I_mag':self.I_mag,'P_Losses':self.P_Losses,'Q_Losses':self.Q_Losses, 
                        'Line_loading': self.Line_loading, 'Tra_loading':self.Trafo_loading}
    
        return self.results, info_network
# %%
