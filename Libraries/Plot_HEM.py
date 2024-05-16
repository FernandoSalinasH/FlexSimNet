#%%
import json
import matplotlib.pyplot as plt
import numpy as np

with open(r"C:\Users\ferna\Desktop\U_Laval\MITACS_Hydro_Quebec\10.Generic_Time_Series_Power_Flow\FlexSimNet\Network_data\Home_Energy_Models_22_Celsius.json", 'r') as f:
            HEM = json.load(f)

x = np.linspace(0, 24, 288)  # 100 points from 0 to 10
for i in range(32):
        results = HEM["electricity"][str(i+1)]
        plt.plot(x, results)

plt.ylabel('[kWh]', fontfamily='cmr10', fontsize=16)
plt.xlabel('Heure',  fontfamily='cmr10', fontsize=16)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tick_params(axis="both", which="both", direction="in", top=True, right=True, labelsize=12)
plt.xlim(0, 24)
plt.show()
