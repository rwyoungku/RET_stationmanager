# Simple test of getting GPS stamp via RS232
# When GPS receives L1 trigger signal from ZCU111 (ZURF)
# it will latch its internal clock values.
# An Arduino MKRZero sits between the F9T and the rPi
# because the easy to use F9T programming library 
# runs only on 32-bit Arduinos. The MKRZero listens
# for the callback of the GPS and will make a local
# copy of the time stamp. If the MKRZero receives a
# capital 'G' from the rPi, it will then return the
# last captured time stamp or a specal code indicating
# there have been no new GPS stamps captured since
# last rPi request.

# The data format returned is an ASCII string ending
# in a /r/n. The rPi will take apart the string and
# extract 5 values.
# count. number of GPS interrupts since last power on
# gps week 
# gps ms into week
# gps ns fraction of ms in to week
# an estimate of accuracy expressed as ns
#
# The special code indicating no new data is the
# value returned for count is -1

# this script has minimal error checking and recovery

import serial
import time
import datetime

#pre compute some things
week2seconds = 7 * 24 * 60 * 60
epochfixup = 315964800.0

#open connection
ser = serial.Serial(
    port='/dev/ttyAMA1',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=10
)

while True :
    #begin polling for new gps data
    #poll at 500ms interval for testing
    #print results
    ser.write(b'G');
    x = ser.readline().decode()
    gps = [int(i) for i in x.split() if i.lstrip('-').isdigit()]
    count = gps[0]
    week = gps[1]
    ms = gps[2]
    ns = gps[3]
    accEst = gps[4]
    if count == -1 :
        pass # nothing to see here, move along
    else:
        # convert to UTC
        seconds = (week * week2seconds) + (ms / 1000.0) + epochfixup + (ns / 1.0e6)
        epoch = time.gmtime(seconds)
        fraction = seconds - int(seconds)
        nice = time.strftime('%Y-%m-%d %H:%M:%S', epoch)
        nice = nice + '.' +  str(int(fraction*1.0e6))
        #print(f'seconds={seconds}')
        print("L1 @", nice)

    time.sleep(0.500) # this should probably be done in a non-blocking fashion


