#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# Define file paths
file_path = r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\Powers.xlsx"
# file_path = r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\Powers_GSO.xlsx"

S = pd.read_excel(file_path, sheet_name='S_power', header=None).iloc[:, 1:]
P_loses = pd.read_excel(file_path, sheet_name='P_losses', header=None).iloc[:, 1:]
Q_loses = pd.read_excel(file_path, sheet_name='Q_losses', header=None).iloc[:, 1:]

S_case11, PL_case11, QL_case11 = S.iloc[1].tolist(), P_loses.iloc[1].tolist(), Q_loses.iloc[1].tolist()
S_case12, PL_case12, QL_case12 = S.iloc[2].tolist(), P_loses.iloc[2].tolist(), Q_loses.iloc[2].tolist()
S_case21, PL_case21, QL_case21 = S.iloc[3].tolist(), P_loses.iloc[3].tolist(), Q_loses.iloc[3].tolist()
S_case22, PL_case22, QL_case22 = S.iloc[4].tolist(), P_loses.iloc[4].tolist(), Q_loses.iloc[4].tolist()

import matplotlib.ticker as ticker

# Assuming each case has 24 data points, one for each hour
time = np.linspace(0, 24, num=288)  # This will generate an array from 1 to 24
# time = np.linspace(0, 24, num=24)  # This will generate an array from 1 to 24

# Set up the matplotlib figure and subplots
fig, axs = plt.subplots(3, 1, figsize=(10, 15))

# Subplot for S_
axs[0].plot(time, S_case11, color = 'black')
axs[0].plot(time, S_case12)
axs[0].plot(time, S_case21)
axs[0].plot(time, S_case22)
axs[0].set_ylabel('S [kVA]', fontfamily='cmr10', fontsize=16)



# Subplot for PL_
axs[1].plot(time, PL_case11, label="Case 1: Comfort 22 [$\degree$C]", color = 'black')
axs[1].plot(time, PL_case12, label="Case 1: Comfort 18 [$\degree$C]")
axs[1].plot(time, PL_case21, label="Case 2: Comfort 22 [$\degree$C]")
axs[1].plot(time, PL_case22, label="Case 2: Comfort 18 [$\degree$C]")

# axs[1].plot(time, PL_case11, label="Scenario 1", color = 'black')
# axs[1].plot(time, PL_case12, label="Scenario 2")
# axs[1].plot(time, PL_case21, label="Scenario 3")
# axs[1].plot(time, PL_case22, label="Scenario 4")

axs[1].legend(prop={'family': 'cmr10', 'size': '14'}, loc = (0.15, 0.32)) # (0.45, 0.4)
# axs[1].set_ylabel('P pertes [kW]',  fontfamily='cmr10', fontsize=16)
axs[1].set_ylabel('P losses [kW]',  fontfamily='cmr10', fontsize=16)


# Subplot for QL_
axs[2].plot(time, QL_case11, color = 'black')
axs[2].plot(time, QL_case12)
axs[2].plot(time, QL_case21)
axs[2].plot(time, QL_case22)
axs[2].set_ylabel('Q losses [kVAr]',  fontfamily='cmr10', fontsize=16)
axs[2].set_xlabel('Hour',  fontfamily='cmr10', fontsize=16)
# axs[2].set_ylabel('Q pertes [kVAr]',  fontfamily='cmr10', fontsize=16)
# axs[2].set_xlabel('Heure',  fontfamily='cmr10', fontsize=16)


for ax in axs.flat:
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlim(0, 24)
    ax.tick_params(axis="both", which="both", direction="in", top=True, right=True, labelsize=12)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(4))  # Set a tick every 1 hour

# Adjust layout to prevent overlap
plt.tight_layout()

# Show plot
plt.show()
