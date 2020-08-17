'''
    Execute this program from the terminal with
     
    $ python3 Fridge-Monitor.py
    
    to read the temperature and position of the BBC Micro:bit placed in the fridge door and connected via BLE to this program. 
    Output the readings to the terminal, and write the temperature and time to a CSV file only when the door is opened or closed 
     
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

from datetime import datetime
import csv
import time
from bluezero import microbit
import math

mcrbt = microbit.Microbit(adapter_addr='RA:SP:BE:RR:YP:I0', # Controller address (Raspberry Pi or PC) that reads from micro:bit. 
                         device_addr='BB:CM:IC:RO:BI:T0', # micro:bit BLE address. Get from $ bluetoothctl or other similar ways.
                         accelerometer_service=False,
                         button_service=True,
                         led_service=False,
                         magnetometer_service=True,
                         pin_service=False,
                         temperature_service=True)

def printVitals(status):
    print( ' Time: ', now, ' Door Closed: ', status, ' Current X: ', mx, ' Closed X: ', closedX,' Temperature: ', celcius)
    
def writeVitals(status):
    writer.writerow([status, now, celcius])

def doorEvent(isClosed):    # A door even happened
    if (doorClosed != isClosed):
        if isClosed:
             printVitals('Closed')
             writeVitals('Closed')
        else:
             printVitals('Open')
             writeVitals('Open')

looping = True
mcrbt.connect()
print('Connected !! Waiting 3 seconds to take first reading')
time.sleep(3) # Wait before taking the first reading
print('Taking readings. Press both buttons to stop monitoring')
doorClosed = False
generalDoorShake = 2
closedX = 0
previousCelcius = 0

with open('/home/username-or-whatever/Desktop/microbit-ble/fridge-livedata-v1-3.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(["Door Position", "Timestamp", "Temperature"])
    while looping:
        now = datetime.now().strftime('%H:%M:%S')
        mx, my, mz = mcrbt.magnetometer
        time.sleep(1) # Wait before taking the temperature
        celcius = mcrbt.temperature

        if closedX == 0: # this is to help the first time the readings are taken. Store the initial door position and mark door as closed
                closedX = mx
                print('Initializing door as closed')
                doorEvent(True) #  Fire a doorEvent() as the door was open before
                doorClosed = True # Mark door as closed.
        if mcrbt.button_a > 0 and mcrbt.button_b > 0:
                looping = False
                print('Exiting.')
        if looping:
                if ( abs(mx)  >= abs(closedX) - abs(generalDoorShake) and abs(mx)  <= abs(closedX) + abs(generalDoorShake)): # door position is within the limits of general shake from closedX. abs value is taken as the sign of closedX could be anything. Means no door event occured
                       #print('WITHIN the limits of general shake. NOT refining closedX')
                       if not doorClosed:
                              print('Marking Door Closed')
                              doorEvent(True)  # Fire a doorEvent() as the door was open before
                       doorClosed = True # Mark door as closed. Not a door event, but just ensuring correct status
                if (celcius < previousCelcius): # is Colder
                       closedX = mx # if the temperature is reducing, refine the closed door position repeatedly. 
                       if not doorClosed:
                              print('Marking Door Closed')
                              doorEvent(True)  # Fire a doorEvent() as the door was open before
                              doorClosed = True # Mark the door as closed as it is not already because the temperature is lowering.       
                       else:
                              printVitals('Lowering')
                              writeVitals('Lowering')                              
                              # Temperature is lowering. Door is closed. Write some logic to track lowest temperature
                #if (celcius >= previousCelcius): print('Same temperature or warmer. Do nothing as we dont know if the door is closed or open')
                if ( abs(mx)  < abs(closedX) - abs(generalDoorShake) or abs(mx)  > abs(closedX) + abs(generalDoorShake)): 
                       # if there's more shake than general shake from closedX
                       print('OUTSIDE the limits of general shake from closedX. Marking door as OPEN')
                       doorEvent(False) # Door is open, fire a doorEvent()
                       doorClosed = False # Mark the door as open
                time.sleep(1) # Wait before taking the next reading
                previousCelcius = celcius # Set previous reading to current value for comparing in the next cycle 
              
mcrbt.disconnect()
