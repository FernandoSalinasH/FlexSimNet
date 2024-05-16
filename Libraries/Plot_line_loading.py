#%% Heatmap
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

# Define file paths
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
    loading_data = pd.read_excel(file_path, sheet_name='Line_loading', header=1).iloc[:, 4:]*100
    all_cases_results[case_name] = loading_data

s1_V_1, s1_V_2, s2_V_1, s2_V_2 = all_cases_results["Case 1_22"], all_cases_results["Case 1_18"], all_cases_results["Case 2_22"], all_cases_results["Case 2_18"]
data = [s1_V_1, s2_V_1, s1_V_2, s2_V_2]

# Create a figure with subplots
fig, axs = plt.subplots(2, 2, figsize=(20, 10)) #, sharex=True)

vmin_f = 0
vmax_f = 120
s1 = axs[0,0].imshow(s1_V_1, plt.cm.get_cmap('jet', 60),vmin=vmin_f, vmax=vmax_f) 
s2 = axs[1,0].imshow(s1_V_2, plt.cm.get_cmap('jet', 60),vmin=vmin_f, vmax=vmax_f) 
s3 = axs[0,1].imshow(s2_V_1, plt.cm.get_cmap('jet', 60),vmin=vmin_f, vmax=vmax_f) 
s4 = axs[1,1].imshow(s2_V_2, plt.cm.get_cmap('jet', 60),vmin=vmin_f, vmax=vmax_f) 
fig.subplots_adjust(wspace=0.,hspace= 0.3)  # Set the spacing between columns to 0.05

fzise = 16

for ax in axs.flat:
    ax.set_yticklabels([])
    ax.tick_params(axis="both", direction="in", length=4, width=0.5, labelsize=14)
    ax.set_ylabel("Lines", fontsize=fzise, rotation=90, va="bottom", fontfamily='cmr10')
    ax.set_aspect('auto')

# Colorbar
cbar = fig.colorbar(s4, ax=axs[:,1], orientation="vertical", aspect=35, pad = 0.01)
cbar.ax.set_ylabel("Loading [%]", fontsize=fzise, rotation=90, labelpad=10, fontfamily='cmr10')
cbar.locator = ticker.MaxNLocator(nbins=10)
cbar.ax.tick_params(labelsize=12, direction="in")
cbar = fig.colorbar(s4, ax=axs[:,0], orientation="vertical", aspect=35, pad = 0.01)
cbar.ax.set_ylabel("Loading [%]", fontsize=fzise, rotation=90, labelpad=10, fontfamily='cmr10')
cbar.locator = ticker.MaxNLocator(nbins=10)
cbar.ax.tick_params(labelsize=12, direction="in")

# Add titles and axis labels

size = 20

axs[0,0].set_title(r"Scenario 1", fontsize=size, fontfamily='cmr10' )
axs[1,0].set_title(r"Scenario 2", fontsize=size, fontfamily='cmr10')
axs[0,1].set_title(r"Scenario 3", fontsize=size, fontfamily='cmr10')
axs[1,1].set_title(r"Scenario 4", fontsize=size, fontfamily='cmr10')

# for i, ax in enumerate(axs.flat):
#     data_flat = all_cases_results[i].values.flatten()
#     max = np.max(data_flat)
#     mean = np.mean(data_flat)
#     sd = np.std(data_flat)
#     over100 = sum(1 for num in data_flat if num > 95)
#     pover100 = (over100 / len(data_flat)) * 100
    
#     ax.text(0.02, 0.5,f"Max = {max:.0f}\nOver 95 = {pover100:.1f}\%", fontsize=12, transform=ax.transAxes, fontfamily='cmr10', ha="left", va="top", color='black')

# Show the plot
plt.show()


# %%
