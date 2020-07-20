'''
    This is a python3 program. Execute from command line with $ python3 ReadAccelerometerAndMagnetometer-WriteToCSV.py
    It reads accelerometer and magnetometer data from a micro:bit via BLE and writes them to a CSV along with some timestamp information 

    Copyright (C) 2020  L Komandur
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
  

'''


import time
import csv
from bluezero import microbit

mcrbt = microbit.Microbit(adapter_addr='RA:SP:BE:RR:YP:I0', # MAC address of Controller (Raspberry Pi or Computer) that reads from micro:bit. This example address is absurd as it has all alphabets
                         device_addr='BB:CM:IC:RO:BI:T0', # BLE MAC address of micro:bit from bluetoothctl or other similar ways. This example address is absurd as it has all alphabets
                         accelerometer_service=True, # Ensure this service is started in MakeCode editor under "on Start" block. Use the HEX file generated to flash onto the micro:bit
                         button_service=True, # Ensure this service is started in MakeCode editor under "on Start" block. Use the HEX file generated to flash onto the micro:bit
                         led_service=False, # Ensure this service is NOT used in MakeCode editor under any block. Use the HEX file generated to flash onto the micro:bit
                         magnetometer_service=True, # Ensure this service is started in MakeCode editor under "on Start" block. Use the HEX file generated to flash onto the micro:bit
                         pin_service=False, # Ensure this service is NOT used in MakeCode editor under any block. Use the HEX file generated to flash onto the micro:bit
                         temperature_service=False) # Ensure this service is not used in MakeCode editor under any block. Use the HEX file generated to flash onto the micro:bit

hasStarted = False # Wait for one of the buttons on the micro:bit to be pressed to start reading
startedAt = 0# To know the timestamp when one of the buttons is pressed to start
fileName ="/home/pi/Desktop/microbit/csv-data/acc-mag-readings-" # File path prefix. It will be appended with startedAt, followed by ".csv" before creating file
face = 0 # Which way is the micro:bit facing? Up face will be assigned 1 and down face will be assigned -1. Maintaining as numbers saves bytes when writing to CSV file
delayBeforeNextReading = 0.25 # If the micro:bit returns 0 values, we dont want to overwhelm it and read again too soon. The delay de-risks connection loss
mcrbt.connect() # Connect to the micro:bit
print('Connected. Press Button A or B to start CSV writing.')
print('Press both buttons to stop and exit.')



# Wait for a button to be pressed to get the time stamp for file name
while not(hasStarted): 
    if mcrbt.button_a > 0 or mcrbt.button_b > 0:
        startedAt = time.time() # store the real start time
        fileName = fileName + str(int(startedAt)) + ".csv" # Form the file name with the start time
        hasStarted = True
    
print('Started At ', int(startedAt))        
print('Readings will be in ', fileName)


with open(fileName, 'w', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(["Face", "Seconds Since Start", "X acc", "Y acc", "Z acc", "X mag", "Y mag", "Z mag"])

    while hasStarted:
        ax, ay, az = mcrbt.accelerometer # Read the accelerometer
        mx, my, mz = mcrbt.magnetometer  # Read the magnetometer
        if not (ax == 0 or ay == 0 or az == 0 or mx == 0 or my == 0 or mz == 0): # Don't try to write anything to file if any of the readings are zero
            if az < 0:
                face = 1
            else:
                face = -1
            # Printing may be used when debugging 
            #print(face, ", Acc X:" , ax, ", Acc Y:" , ay, ", Acc Z:" , az, ", Mag X:", mx,", Mag Y:",  my,", Mag Z:",  mz)
            writer.writerow([face, time.time() - startedAt, ax, ay, az, mx, my, mz])
        else:
            print('Reading skipped. Delaying ', str(delayBeforeNextReading), ' seconds to attempt again')
            time.sleep(delayBeforeNextReading)
            
        if mcrbt.button_a > 0 and mcrbt.button_b > 0:
            hasStarted = False # This means to loop needs to be stopped for exiting
            print('Exiting')

mcrbt.disconnect()
