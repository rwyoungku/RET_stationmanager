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
import glob
import os

#change this as needed to use the correct UART
uart = '/dev/ttyAMA1'

#pre compute some things
week2seconds = 7 * 24 * 60 * 60
epochfixup = 315964800.0

# it is possible to have a very old time stamp
# trapped in the MkrZero buffer
# it might be a good idea to itnore the
# first time stamp
first_time = 1

# filename generation stuff
# check for data subdirectory
os.makedirs('data', exist_ok=True)

try:
    #look into directory and try and find the last file written
    LatestFile = max(glob.iglob('data/*.dat'),key=os.path.getctime)
    #extract the file number using our name_######.dat convention
    temp = LatestFile.partition("_")[2].partition('.')[0]
    lastindex = int(temp)
except:
    lastindex = 0

filename = "data/L1_"
filename_counter = lastindex+1

# test data
dummy_data = []
dummy_data = [0 for i in range(4096)] 

#open serial connection
ser = serial.Serial(
    port = uart,
    baudrate = 115200,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1  #in seconds
)

# clear buffers in case there is stale data
ser.reset_input_buffer()
ser.reset_output_buffer()

while True :
    #begin polling for new gps data
    #poll at 500ms interval for testing
        #print results
    ser.write(b'G');
    try:
        x = ser.readline().decode()
        gps = [int(i) for i in x.split() if i.lstrip('-').isdigit()]
        if len(gps) == 5:
            count = gps[0]
            week = gps[1]
            ms = gps[2]
            ns = gps[3]
            accEst = gps[4]
        else:
            count = -1 #error, insufficient data
    except:
        count = -1

    if count == -1 :
        pass # nothing to see here, move along
    else:
        if first_time == 1:
            #probably stale data
            first_time = 0
            print("Stale data in MKRZero buffer")
        else:
            # convert to UTC
            seconds = (week * week2seconds) + (ms / 1000.0) + epochfixup + (ns / 1.0e6)
            epoch = time.gmtime(seconds)
            fraction = seconds - int(seconds)
            nice = time.strftime('%Y-%m-%d %H:%M:%S', epoch)
            nice = "L1 @ " + nice + '.' +  str(int(fraction*1.0e6))
            print(nice)

            fn = filename + f'{filename_counter:06d}' + ".dat"
            with open(fn, 'a') as f: # open in append mode please
                f.write('\n\n'+nice+'\n')
                f.write(x + '\n')
                f.write(str(dummy_data))
                f.write('\n\n')

            counter = counter + 1

    time.sleep(0.500) # this should probably be done in a non-blocking fashion


