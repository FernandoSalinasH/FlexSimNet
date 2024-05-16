#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# Define file paths
file_path = r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\Powers.xlsx"
single = pd.read_excel(file_path, sheet_name='P_User_single', header=None).iloc[:, 2:]
multi = pd.read_excel(file_path, sheet_name='P_User_multi', header=None).iloc[:, 2:]

Load_case11_s, Line_case11_s = single.iloc[2].tolist(), single.iloc[1].tolist()
Load_case12_s, Line_case12_s = single.iloc[4].tolist(), single.iloc[3].tolist()
Load_case21_s, Line_case21_s, EV_case21_s, PV_case21_s, St_case21_s = single.iloc[6].tolist(), single.iloc[5].tolist(), single.iloc[7].tolist(), single.iloc[8].tolist(), single.iloc[9].tolist()
Load_case22_s, Line_case22_s, EV_case22_s, PV_case22_s, St_case22_s = single.iloc[11].tolist(), single.iloc[10].tolist(), single.iloc[12].tolist(), single.iloc[13].tolist(), single.iloc[14].tolist()

Load_case11_m, Line_case11_m = multi.iloc[2].tolist(), multi.iloc[1].tolist()
Load_case12_m, Line_case12_m = multi.iloc[4].tolist(), multi.iloc[3].tolist()
Load_case21_m, Line_case21_m, EV_case21_m, PV_case21_m, St_case21_m = multi.iloc[6].tolist(), multi.iloc[5].tolist(), multi.iloc[7].tolist(), multi.iloc[8].tolist(), multi.iloc[9].tolist()
Load_case22_m, Line_case22_m, EV_case22_m, PV_case22_m, St_case22_m = multi.iloc[11].tolist(), multi.iloc[10].tolist(), multi.iloc[12].tolist(), multi.iloc[13].tolist(), multi.iloc[14].tolist()

import matplotlib.ticker as ticker
size_title = 14
size_label = 14
# Assuming each case has 24 data points, one for each hour
time = np.linspace(0, 24, num=288)  # This will generate an array from 1 to 24

# Set up the matplotlib figure and subplots
fig, axs = plt.subplots(5, 2, figsize=(10, 15))

# Subplot for Lines
axs[0,0].plot(time, Line_case11_s)
axs[0,0].plot(time, Line_case12_s)
axs[0,0].plot(time, Line_case21_s)
axs[0,0].plot(time, Line_case22_s)
axs[0,0].set_title('Power Supply',  fontfamily='Arial', fontsize=size_title)
# axs[0,0].set_title('Alimentation Électrique',  fontfamily='Arial', fontsize=size_title)
axs[0,0].set_ylabel('[kW]', fontfamily='Arial', fontsize=size_label)

axs[0,1].plot(time, Line_case11_m)
axs[0,1].plot(time, Line_case12_m)
axs[0,1].plot(time, Line_case21_m)
axs[0,1].plot(time, Line_case22_m)
axs[0,1].set_title('Power Supply',  fontfamily='Arial', fontsize=size_title)
# axs[0,1].set_title('Alimentation Électrique',  fontfamily='Arial', fontsize=size_title)
axs[0,1].set_ylabel('[kW]', fontfamily='Arial', fontsize=size_label)

# Subplot for Loads
axs[1,0].plot(time, Load_case11_s)
axs[1,0].plot(time, Load_case12_s)
axs[1,0].plot(time, Load_case21_s)
axs[1,0].plot(time, Load_case22_s)
axs[1,0].set_title('Load Profile',  fontfamily='Arial', fontsize=size_title)
# axs[1,0].set_title('Profil de Charge',  fontfamily='Arial', fontsize=size_title)
axs[1,0].set_ylabel('[kW]', fontfamily='Arial', fontsize=size_label)

axs[1,1].plot(time, Load_case11_m)
axs[1,1].plot(time, Load_case12_m)
axs[1,1].plot(time, Load_case21_m)
axs[1,1].plot(time, Load_case22_m)
axs[1,1].set_title('Load Profile',  fontfamily='Arial', fontsize=size_title)
# axs[1,1].set_title('Profil de Charge',  fontfamily='Arial', fontsize=size_title)
axs[1,1].set_ylabel('[kW]', fontfamily='Arial', fontsize=size_label)

# Get the current color cycle
default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
# Skip the first two colors

colors_skip = default_colors[2:]  # This starts from the third color
# Subplot for EV
axs[2,0].plot(time, EV_case21_s, color=colors_skip[0])
axs[2,0].plot(time, EV_case22_s, color=colors_skip[1])
axs[2,0].set_title('Electric Vehicle',  fontfamily='Arial', fontsize=size_title)
# axs[2,0].set_title('Véhicule électrique',  fontfamily='Arial', fontsize=size_title)
axs[2,0].set_ylabel('[kW]', fontfamily='Arial', fontsize=size_label)

axs[2,1].plot(time, EV_case21_m, color=colors_skip[0])
axs[2,1].plot(time, EV_case22_m, color=colors_skip[1])
axs[2,1].set_title('Electric Vehicle',  fontfamily='Arial', fontsize=size_title)
# axs[2,1].set_title('Véhicule électrique',  fontfamily='Arial', fontsize=size_title)
axs[2,1].set_ylabel('[kW]', fontfamily='Arial', fontsize=size_label)

# Subplot for PV
axs[3,0].plot(time, PV_case21_s, color=colors_skip[0])
axs[3,0].plot(time, PV_case22_s, color=colors_skip[1])
axs[3,0].set_title('PV System',  fontfamily='Arial', fontsize=size_title)
# axs[3,0].set_title('Système PV',  fontfamily='Arial', fontsize=size_title)
axs[3,0].set_ylabel('[kW]', fontfamily='Arial', fontsize=size_label)

axs[3,1].plot(time, PV_case21_m, color=colors_skip[0])
axs[3,1].plot(time, PV_case22_m, color=colors_skip[1])
axs[3,1].set_title('PV System',  fontfamily='Arial', fontsize=size_title)
# axs[3,1].set_title('Système PV',  fontfamily='Arial', fontsize=size_title)
axs[3,1].set_ylabel('[kW]', fontfamily='Arial', fontsize=size_label)

# Subplot for storage
axs[4,0].plot(time, St_case21_s, color=colors_skip[0])
axs[4,0].plot(time, St_case22_s, color=colors_skip[1])
axs[4,0].set_title('Storage System',  fontfamily='Arial', fontsize=size_title)
# axs[4,0].set_title('Système de Stockage',  fontfamily='Arial', fontsize=size_title)
axs[4,0].set_ylabel('[kW]', fontfamily='Arial', fontsize=size_label)
axs[4,0].set_xlabel('Time [hours]',  fontfamily='Arial', fontsize=size_label)
# axs[4,0].set_xlabel('Heure',  fontfamily='Arial', fontsize=size_label)

axs[4,1].plot(time, St_case21_m, color=colors_skip[0])
axs[4,1].plot(time, St_case22_m, color=colors_skip[1])
axs[4,1].set_title('Storage System',  fontfamily='Arial', fontsize=size_title)
# axs[4,1].set_title('Système de Stockage',  fontfamily='Arial', fontsize=size_title)
axs[4,1].set_ylabel('[kW]', fontfamily='Arial', fontsize=size_label)
axs[4,1].set_xlabel('Time [hours]',  fontfamily='Arial', fontsize=size_label)
# axs[4,1].set_xlabel('Heure',  fontfamily='Arial', fontsize=size_label)

fig.text(0.27, 0.97, "Single-family building", ha="center", fontweight="bold", fontsize=14, fontfamily='Times New Roman', fontstyle= 'italic')
fig.text(0.76, 0.97, "Multi-family building", ha="center", fontweight="bold", fontsize=14, fontfamily='Times New Roman', fontstyle= 'italic')
# fig.text(0.27, 0.97, "Bâtiments Unifamiliaux", ha="center", fontweight="bold", fontsize=16, fontfamily='Times New Roman', fontstyle= 'italic')
# fig.text(0.77, 0.97, "Bâtiments Multifamiliaux", ha="center", fontweight="bold", fontsize=16, fontfamily='Times New Roman', fontstyle= 'italic')

for ax in axs.flat:
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlim(0, 24)
    ax.tick_params(axis="both", which="both", direction="in", top=True, right=True, labelsize=12)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(4))  # Set a tick every 1 hour


fig.legend(['Case 1: Comfort 22 [$\degree$C]', 'Case 1: Comfort 18 [$\degree$C]','Case 2: Comfort 22 [$\degree$C]', 'Case 2: Comfort 18 [$\degree$C]'], loc='lower center', ncol=4)
# fig.legend(['Scenario 1', 'Scenario 2','Scenario 3', 'Scenario 4'], loc='lower center', ncol=4, prop={'family': 'Arial', 'size': '10'})


# Adjust layout to prevent overlap
plt.tight_layout()

# Show plot
plt.show()
