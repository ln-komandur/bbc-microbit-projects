'''
    Execute this program from the terminal with
     
    $ python3 Fridge-Monitor.py
    
    to read the temperature and position of the BBC Micro:bit placed in the fridge door and connected via BLE to this program,
    output the readings to the terminal, and write the temperature upon door opening and closing in a CSV file
     
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
                         device_addr='BB:CM:IC:RO:BI:T0', # micro:bit BLE address. Get from bluetoothctl or other similar ways.
                         accelerometer_service=True,
                         button_service=True,
                         led_service=False,
                         magnetometer_service=True,
                         pin_service=False,
                         temperature_service=True)

looping = True
started = True
mcrbt.connect()
print('Connected !! Monitoring started. Press both buttons A & B to exit')

doorClosed = False
inherentShakeFactor = 2
closedXYZ = 0
previousCelcius = 0

with open('/home/pi/Desktop/microbit/csv-data/fridge-livedata.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(["Door", "Timestamp", "Temperature"])

    while looping:
        if mcrbt.button_a > 0 or mcrbt.button_b > 0:
                started = True
        if mcrbt.button_a > 0 and mcrbt.button_b > 0:
                looping = False
                started = False
                print('Exiting.')
        if started:
                now = datetime.now().strftime('%H:%M:%S')
                ax, ay, az = mcrbt.accelerometer
                mx, my, mz = mcrbt.magnetometer
                celcius = mcrbt.temperature
                currentXYZ =  round(math.sqrt(mx*mx + my * my + mz * mz))
                if closedXYZ == 0:
                        closedXYZ = currentXYZ
                print('Curr XYZ ',currentXYZ, ' Closed XYZ', closedXYZ, ' Prev Celcius ', previousCelcius, ' Curr Celcius ', celcius, ' Door ', doorClosed)
                if celcius > previousCelcius:
                        doorClosed = False
                elif celcius < previousCelcius:
                        closedXYZ = currentXYZ
                        if not doorClosed:
                                doorClosed = True
                                print('Door is now Closed. XYZ ', closedXYZ, ' Time ', now, ' Temperature ', celcius)
                                writer.writerow(["Closed", now, celcius])

                if doorClosed and ( currentXYZ  < (closedXYZ - inherentShakeFactor) or currentXYZ  > (closedXYZ + inherentShakeFactor)):
                        print('Door is now Open. XYZ ', closedXYZ, ' Time ', now, ' Temperature ', celcius)
                        writer.writerow(["Open", now, celcius])
                        doorClosed = False
                previousCelcius = celcius
                time.sleep(1)
mcrbt.disconnect()
