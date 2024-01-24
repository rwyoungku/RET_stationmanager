import serial
import time
import math
import csv
from sys import platform

if __name__ == "__main__" :
    if platform == "win32" :
        uart = "COM4"
    else :
        uart = '/dev/ttyAMA1' # should be UART3

    bps = 115200
    tout = 1

    ser = serial.Serial(
        port = uart, 
        baudrate = bps, 
        parity = serial.PARITY_NONE, 
        stopbits = serial.STOPBITS_ONE, 
        bytesize = serial.EIGHTBITS, 
        timeout = tout
    )

    #clear buffeers
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    ser.write("id\r\n".encode())
    ver = ser.readline().decode("utf-8")
    print(ver)

    # turn on all 8
    for ch in range(1,9):
        cmd = "control " + str(ch) + " 1\r\n"
        print(cmd)
        ser.write(cmd.encode())
        time.sleep(0.5)

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    while ser.in_waiting > 0 :
        ser.read()

    RTD_A  = 3.9083e-3
    RTD_B  = -5.775e-7
    RREF = 400.0
    RTDnominal = 100.0

    filename = "tempdata.csv"
    
    # The RF power supply board now has a 10 minute WDT
    # that resets every time a valid command is received
    # There is a command "DOG" which simply kicks the
    # watchdog and does not return anything. Or as below
    # the "TEMP" command can be used to read the RTD 
    # sensor on a regular basis. Rather than have the 
    # ATMEGA328 processor compute the temperature in Celsius,
    # it is returned as a raw sample and the data is 
    # converted in the Python code on the rPi.

    try :
        while True :
            cmd = "temp\r\n"
            ser.write(cmd.encode())
            str_rtd = ser.readline().decode("utf-8")
            tries = 0
            while True :
                if (not(str_rtd and str_rtd.strip())) :
                    print("Err, rtd = " + str_rtd)
                    ser.write(cmd.encode())
                    str_rtd = ser.readline().decode("utf-8")
                else :
                    break

                tries = tries + 1
                if (tries == 10) :
                    str_rtd = "0"
                    break
                else :
                    break
            t = time.localtime()
            #print(str_rtd, end=" ", flush=True)
            rtd = int(str_rtd)
            rt = float(rtd)
            rt = rt / 32768
            rt = rt * RREF
            Z1 = -RTD_A
            Z2 = RTD_A * RTD_A - (4 * RTD_B)
            Z3 = (4 * RTD_B) / RTDnominal
            Z4 = 2 * RTD_B
            temp = Z2 + (Z3 * rt)
            temp = (math.sqrt(temp) + Z1) / Z4;
            temp = round(temp, 2)
            row = [time.strftime("%b-%d-%Y", t), time.strftime("%H:%M:%S", t), temp]
            print(row)
            with open(filename, "a", encoding="utf-8") as f:
                writer=csv.writer(f)
                writer.writerow(row)
            for i in range(1,11) :
                print((11-i), end=" ", flush=True)
                time.sleep(1)
            print(" ")
    except KeyboardInterrupt :
        pass

    ser.write("rst\r\n".encode())
    ser.close()

