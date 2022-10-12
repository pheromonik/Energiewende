import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from readData import *

properties = dict(())
properties['Biomasse'] = 1
properties['Wasserkraft'] = 1
#properties['WindOff'] = 7.864
#properties['WindOn'] = 57.459
#properties['Photovoltaik'] = 63.523
properties['WindOff'] = 65.0
properties['WindOn'] = 150.0
properties['Photovoltaik'] = 350.0
properties['SonstigeE'] = 1
properties['Kernenergie'] = 0
properties['Braunkohle'] = 0
properties['Steinkohle'] = 0
properties['Erdgas'] = 0
properties['SonstigeK'] = 0

current_month_key = str(datetime.strptime(str(8) + "." + str(2022), '%m.%Y'))
  
electricity_data = read_creation_usage()

installed_power = read_installed_power()

max_storage_power_per_quarter_hour = 40.00
max_storage_capacity = 5000.0

sharesOnConsumption = list(())
shares_with_missing_energy = list(())
dumped_energy = 0.0
total_produced_energy = 0.0

stored_energy = 20.0

times_without_storage = 0

for date_string,entry in electricity_data.items():
  date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
  month_date_key = str(datetime.strptime(str(date.month) + "." + str(date.year), '%m.%Y'))
  
  try:
    installed = installed_power[month_date_key]
  except KeyError:
    installed = installed_power[current_month_key]
    
  calculated_energy = 0.0
  for name,value in properties.items():
    try:
      factor = value/installed[name]
    except KeyError:
      factor = value
      
    production = entry[name] * factor
    calculated_energy += production
    
  total_produced_energy += calculated_energy
    
  consumption = entry["Netzlast"]
  
  surplus = calculated_energy - consumption
  
  net_energy_production_after_storage = calculated_energy
  
  newly_stored_energy = 0.0
  
  if surplus > 0:
    # Store electricity if possible
    free_storage = max_storage_capacity - stored_energy
    newly_stored_energy = min(surplus, free_storage, max_storage_power_per_quarter_hour)
    net_energy_production_after_storage -= newly_stored_energy
      
    dumped_energy += surplus - newly_stored_energy
    stored_energy += newly_stored_energy * 0.8
  else:
    # Use storage if possible
    used_storage = min(stored_energy, max_storage_power_per_quarter_hour, surplus * (-1.0))
    net_energy_production_after_storage += used_storage
    stored_energy -= used_storage # used storage cannot be larger than stored energy, so this never goes below 0
    
  if stored_energy < 0:
    print("Something is wrong")
  
  share = (net_energy_production_after_storage/consumption) * 100
  if share < 99:
    times_without_storage += 1
    print(date_string)
    print(entry)
    print(calculated_energy)
    print(net_energy_production_after_storage)
    print(consumption)
    print(surplus)
    print(stored_energy)
    shares_with_missing_energy.append(share)
    
  sharesOnConsumption.append(share)
    
    
print("Dumped Energy percentage: " + str(dumped_energy/total_produced_energy * 100.0))
print(times_without_storage)
print(min(sharesOnConsumption))
print(max(sharesOnConsumption))
print(total_produced_energy/1000)
#plt.hist(shares_with_missing_energy, density=True, bins=44)
#plt.show() 
      
    

      
