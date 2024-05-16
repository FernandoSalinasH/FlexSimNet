#%% Boxplot
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
    loading_data = pd.read_excel(file_path, sheet_name='Tra_loading', header=1).iloc[:, 2:]*100
    all_cases_results[case_name] = loading_data

# Create a figure with subplots
fig, axs = plt.subplots(2, 2, figsize=(20, 10), sharex=False, sharey= True)
axs = axs.flatten()  # Flatten to make iteration easier

case_titles = ["Scenario 1", "Scenario 2", "Scenario 3", "Scenario 4"]

# Iterate over each case and plot
for idx, (case_name, results) in enumerate(all_cases_results.items()):
    
    data_for_boxplot = results
    
    # Plot boxplot
    box = axs[idx].boxplot(data_for_boxplot, showfliers=False, patch_artist=True, positions=np.arange(1, 25))
    
    color1= '#ffd447'
    color2='#d4a200'
    # Set all boxes to the same color, e.g., light blue
    for patch in box['boxes']:
        patch.set_facecolor(color1)  # Set all boxes to light blue
        patch.set_edgecolor(color2) 
    
    # Optionally, customize whiskers, fliers, caps, and the median line
    for whisker in box['whiskers']:
        whisker.set(color =color2, linewidth = 1)
    for cap in box['caps']:
        cap.set(color =color2, linewidth = 1)
    for median in box['medians']:
        median.set(color =color2, linewidth = 1)
    # for flier in box['fliers']:
    #     flier.set(marker ='o', color ='yellow', alpha = 0.5)
        
    axs[idx].set_title(case_titles[idx], fontsize=18, fontfamily='cmr10')
    axs[idx].set_ylabel('Niveaux de charge [%]', fontsize=14, fontfamily='cmr10')
    axs[idx].tick_params(axis="x", labelsize=12)
    axs[idx].tick_params(axis="y", labelsize=12)
    axs[idx].grid(True, linestyle="--", alpha=0.5)
    
    # Set x-ticks to be more meaningful
    hours = np.arange(1, 25)  # Assuming 24 hours starting from 1 to 24
    axs[idx].set_xticks(hours)

for idx, (case_name, results) in enumerate(all_cases_results.items()):
    data_flat = results.values.flatten()
    mean_val = np.mean(data_flat)  # Similarly for 'mean'
    over100 = sum(1 for num in data_flat if num > 95)
    pover100 = (over100 / len(data_flat)) * 100
    
    # Use 'axs[idx]' instead of 'idx' to access the axis object for annotations
    axs[idx].text(0.2, 0.96, f"Moyenne = {mean_val:.0f}%\n\n(> 95 %)  = {pover100:.1f}%", fontsize=12, transform=axs[idx].transAxes, fontfamily='Arial', ha="left", va="top", color='black')


plt.tight_layout()
plt.show()