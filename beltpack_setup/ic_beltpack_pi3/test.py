##LED WIFI indicator
import subprocess
import time
import argparse
import re
from shiftpi import HIGH, LOW, digitalWrite, delay, shiftRegisters, ALL
import RPi.GPIO as GPIO
##Set all the LEDs up
GPIO.setmode(GPIO.BCM)
## Set three shift registers
shiftRegisters(3)
## The pinList is chao!tic because of my inattenttion but so what..its a software fix!
pinList = [16,17,18,19,20,21,22,23,24,8,9,10,11,12,13,14,15,0,7,6,5,4,3,1,2]

print '\n---Press CTRL+Z or CTRL+C to stop.---\n'
##Set the LEDs to Off
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
digitalWrite(ALL,LOW)

def scan_wlan0_for_quality():
    cmd = subprocess.Popen('iwconfig ' 'wlan0', shell=True,
                           stdout=subprocess.PIPE)
    for line in cmd.stdout:
        if 'Link Quality' in line:
            yikes = line.lstrip(' ')
            ##Pull the signal strength out
            wifi_level = re.findall(r'([0-9][0-9])',yikes)
            raw_level = wifi_level[0]
            ##Convert it to a percentage
            percent_level = (float(raw_level)/70)*100
            value = int(percent_level)
            return value
    return 0

def output_led( lightLED):
   for index in range(0,lightLED):
        if lightLED == 25:
            ##Light all the LEDs because the WIFI siganl is 100%
            digitalWrite(ALL,HIGH)
            GPIO.output(18,GPIO.HIGH)
        else:
            ##Light the number of LEDs equal to the WIFI signal strength
            digitalWrite(pinList[index], HIGH)
            GPIO.output(18,GPIO.LOW)

class Average:
    def __init__(self, depth = 10):
        self.depth = 10
        self.values = []
        
    def addValue(self, value):
        self.values.append(value)
        # truncate to depth
        if len( self.values) > self.depth:
            self.values = self.values[ 1:]
            
    def getAverage(self):
        # no data, no average.
        if len( self.values ) == 0:
            return 0
        return sum( self.values) / len(self.values)
     
average = Average()       
         
while True:
    value = scan_wlan0_for_quality()

    average.addValue( value)
    # added brackets for python3-compatibility
    print ("Siganal percecnt: ", value, average.getAverage() )
    ##Convert it to a value for the LED array
    lightLED = int(value/5)
    print (lightLED)
    output_led(lightLED)
    time.sleep(0.5)

digitalWrite(ALL,LOW)
GPIO.cleanup