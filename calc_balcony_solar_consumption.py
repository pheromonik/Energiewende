import json
from datetime import datetime
from datetime import timezone
import pytz

time_format = "%Y-%m-%d %H:%M:%S %Z%z"
local_time_zone = 'Europe/Berlin'

f = open("Timeseries_48.546_9.058_SA2_0kWp_crystSi_10_90deg_0deg_2020_2020.json")

data = json.loads(f.read())
time_data = data["outputs"]["hourly"]
# Date from https://re.jrc.ec.europa.eu/pvg_tools/en/

base_load = 13
work_load = 50
tv_load = 50

minute_power = 100
minute_energy_consumption = 40

total_produced_energy = 0.0
total_used_energy = 0.0
for hourly_data in time_data:
  utc_time = datetime.strptime(hourly_data["time"], "%Y%m%d:%H%M").replace(tzinfo=timezone.utc)
  local_time = utc_time.astimezone(pytz.timezone(local_time_zone))
  power = float(hourly_data["P"])
  if power == 0.0:
    continue
  
  total_produced_energy += power
  
  # Base load (router and stuff)
  used_energy = min(power,base_load)
  total_used_energy += used_energy
  power -= used_energy
  
  isoweekday = local_time.isoweekday()
  hour = local_time.hour
  # Work and play
  if isoweekday in (1,2,5,7):
    if hour >= 8 and hour <= 20 and hour not in (12,13):
      used_energy = min(power,work_load)
      total_used_energy += used_energy
      power -= used_energy
      
  # TV
  if isoweekday != 1:
    if hour > 12 and hour < 20:
      used_energy = min(power,tv_load)
      total_used_energy += used_energy
      power -= used_energy
   
  minute_energy_consumption_current = 0.0
  # Minute load
  for minute in range(60):
    if minute_energy_consumption_current < minute_energy_consumption:
      
      minute_used_energy = min(power,minute_power)/60
      minute_energy_consumption_current += minute_used_energy
      
      total_used_energy += minute_used_energy
      
  #print(minute_energy_consumption_current)
  
print(total_used_energy)
print(total_used_energy/total_produced_energy)
print(total_used_energy/1000.0 * 0.25)
