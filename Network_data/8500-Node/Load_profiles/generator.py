
#%%

with open(r"C:\Users\ferna\OneDrive\Desktop\U_Laval\MITACS_Hydro_Quebec\10.PowerFLow\opendsswindows\Network_data\123Bus\Load_profiles\load_profile_40.txt", 'r') as f:
    content = f.read() 
for i in range(1,2354+1):
    with open(r'C:\Users\ferna\OneDrive\Desktop\U_Laval\MITACS_Hydro_Quebec\10.PowerFLow\opendsswindows\Network_data\8500-Node\Load_profiles\load_profile_'+ str(i) +'.txt','w+') as m:
        m.write(content) #creates a txt file to save all created monitors
        #m.write('\n')\
        m.close()
