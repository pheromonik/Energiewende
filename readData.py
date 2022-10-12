import csv
from datetime import datetime

properties = {
  2:"Biomasse",
  3:"Wasserkraft",
  4:"WindOff",
  5:"WindOn",
  6:"Photovoltaik",
  7:"SonstigeE",
  8:"Kernenergie",
  9:"Braunkohle",
  10:"Steinkohle",
  11:"Erdgas",
  #12:"PumpspeicherCreation",
  13:"SonstigeK",
  14:"Netzlast"
  #16:"PumpspeicherUsage"
}

properties_installed_power = {
  1:"WindOff",
  2:"WindOn",
  3:"Photovoltaik"
}

def read_creation_usage():
  return read_csv('Smard_Data.csv', ';', "%d.%m.%Y%H:%M", properties, {0,1})

def read_installed_power():      
  return read_csv('energy-charts_Net_installed_electricity_generation_capacity_in_Germany.csv', ',', "%m.%Y", properties_installed_power, {0})

def read_csv(fileName, delimiter, dateformat, properties, joins_for_date_key):
  data = dict(())
  
  last_key = ''
  with open(fileName, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=delimiter, quotechar='"')
    next(reader, None) #Skip header
    
    for row in reader:
      entry = dict(())
      raw_date_string = ""
      for row_number in joins_for_date_key:
        raw_date_string = raw_date_string + row[row_number]
        
      key=str(datetime.strptime(raw_date_string,dateformat))
      for propPosition,propName in properties.items():
        raw_entry_value = row[propPosition]
        
        value = 0
        if raw_entry_value != '':
          # Get value in GW. Values above 1 GW are given in the format "1.204", but it can also be something like "1.2". This conversion catches both versions
          try:
            value=int(raw_entry_value)/1000.0
            try:
              last_value = data[last_key][propName]
            except KeyError:
              last_value = 0.0
              
            if propName == "Netzlast" or (value < 0.05 and last_value > 1.0):
              # consumption never gets below 1 GWh OR
              # Check if last entry was 1 GWh or higher and this value is 0.05 or lower - then we most probably have a data problem
              value = value * 1000.0
              #if propName != "Netzlast":
                #print("Assuming problem with property " + propName + " in " + str(row))
                #print("Correcting value, multiply by 1000, GWh assumed instead of MWh")

          except ValueError:
            value=float(raw_entry_value) 
          
        entry[propName] = value
      
      data[key] = entry
      last_key = key
      
  return data
