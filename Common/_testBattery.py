
from ev3dev.ev3 import PowerSupply

# Create an instance of the PowerSupply class
power = PowerSupply()

# Get the battery voltage
# convert from microvolts to volts
voltage = power.measured_voltage / 10e5

# Get the battery current
# converts from microamps to amps
current = power.measured_current / 10e5

# Get the battery capacity
capacity = None
#capacity = power.measured_amps / 1000.0  # Convert mAh to Ah

# Print the results
print("Battery Voltage:", voltage, "V")
print("Battery Current:", current, "A")
#print("Battery Capacity:", capacity, "Ah")
