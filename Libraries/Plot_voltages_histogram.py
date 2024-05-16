#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# Define file paths
# file_paths = {
#     "Case 1_22": r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\Case_study_1_22C.xlsx",
#     "Case 1_18": r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\Case_study_1_18C.xlsx",
#     "Case 2_22": r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\Case_study_2_22C.xlsx",
#     "Case 2_18": r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\Case_study_2_18C.xlsx"
# }

file_paths = {
    "Case 1_22": r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\GSO_original.xlsx",
    "Case 1_18": r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\GSO_HEM_22.xlsx",
    "Case 2_22": r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\GSO_HEM_18.xlsx",
    "Case 2_18": r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Results_paper_FlexSimNet\GSO_HEM_22_EV.xlsx"
}

# Initialize a dictionary to store the results
all_cases_results = {}

# Load data for each case
for case_name, file_path in file_paths.items():
    # Adjust as necessary if the 'Voltage' sheet has a different name or structure
    voltage_data = pd.read_excel(file_path, sheet_name='Voltage', header=1).iloc[:, 1:]
    all_cases_results[case_name] = voltage_data.values.flatten()

s1_V_1, s1_V_2, s2_V_1, s2_V_2 = all_cases_results["Case 1_22"], all_cases_results["Case 1_18"], all_cases_results["Case 2_22"], all_cases_results["Case 2_18"]
data = [s1_V_1, s2_V_1, s1_V_2, s2_V_2]

#%%

# Create a figure with subplots
fig, axs = plt.subplots(2, 2, figsize=(20, 14), sharex=False, sharey=False)

# axs[0,0].hist(s1_V_1, bins=np.linspace(0.90, 1.1, num=50), color="#87CEFA", edgecolor="black")
# axs[1,0].hist(s1_V_2, bins=np.linspace(0.90, 1.1, num=50), color="#87CEFA", edgecolor="black")
# axs[0,1].hist(s2_V_1, bins=np.linspace(0.80, 1.15, num=50), color="#FFE873", edgecolor="black")
# axs[1,1].hist(s2_V_2, bins=np.linspace(0.80, 1.15, num=50), color="#FFE873", edgecolor="black")

min = 0.96
max = 1.05
axs[0,0].hist(s1_V_1, bins=np.linspace(min, max, num=50), color="#87CEFA", edgecolor="black")
axs[1,0].hist(s1_V_2, bins=np.linspace(min, max, num=50), color="#87CEFA", edgecolor="black")
axs[0,1].hist(s2_V_1, bins=np.linspace(min, max, num=50), color="#FFE873", edgecolor="black")
axs[1,1].hist(s2_V_2, bins=np.linspace(min, max, num=50), color="#FFE873", edgecolor="black")

fig.subplots_adjust(wspace=0.15, hspace=0.6)  # Set the spacing between columns to 0.05
means = []
for ax, y in zip(axs.flat, data):
    ax.annotate(f"Moyenne = {y.mean():.3f}", xy=(0.05, 0.95), xycoords="axes fraction", fontsize=16, fontfamily='cmr10', ha="left", va="top")
    ax.annotate(f"Ecart Type = {y.std():.3f}", xy=(0.05, 0.85), xycoords="axes fraction", fontsize=16, fontfamily='cmr10', ha="left", va="top")
    means.append(y.mean())

# Add titles and axis labels

size = 20
# axs[0,0].set_title(r"Case Study 1: Comfort 22 [$\degree$C]", fontsize=size, fontfamily='cmr10' )
# axs[1,0].set_title(r"Case Study 1: Comfort 18 [$\degree$C]", fontsize=size, fontfamily='cmr10')
# axs[0,1].set_title(r"Case Study 2: Comfort 22 [$\degree$C]", fontsize=size, fontfamily='cmr10')
# axs[1,1].set_title(r"Case Study 2: Comfort 18 [$\degree$C]", fontsize=size, fontfamily='cmr10')

axs[0,0].set_title(r"Scenario 1", fontsize=size, fontfamily='cmr10' )
axs[1,0].set_title(r"Scenario 2", fontsize=size, fontfamily='cmr10')
axs[0,1].set_title(r"Scenario 3", fontsize=size, fontfamily='cmr10')
axs[1,1].set_title(r"Scenario 4", fontsize=size, fontfamily='cmr10')

def kilo(x, pos):
    return '%1.0fk' % (x * 1e-3)
formatter = FuncFormatter(kilo)

for ax, y in zip(axs.flat, data):
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.tick_params(axis="both", which="both", direction="in", top=True, right=True, labelsize=12)
    ax.set_ylabel("Occurrence [#]", fontsize=16, fontfamily='cmr10')
    ax.axvline(x = y.mean(), color='red', linestyle='--', linewidth=2) # draws the vertical line
    ax.yaxis.set_major_formatter(formatter)

axs[1,0].set_xlabel('Tension [pu]', fontsize=size, fontfamily='cmr10')
axs[1,1].set_xlabel('Tension [pu]', fontsize=size, fontfamily='cmr10')

# Show the plot
plt.show()


# %%
