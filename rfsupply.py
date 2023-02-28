import serial
import time

#change this as needed to use the correct UART
uart = '/dev/ttyAMA1' # should be UART3 if it is the only extra one enabled

#open serial connection
ser = serial.Serial(
    port = uart,
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1  #in seconds
)

# clear buffers in case there is stale data
ser.reset_input_buffer()
ser.reset_output_buffer()

error_count = 0

# get the version number and display
bytes = bytearray()
bytes.append(0x56) # V
bytes.append(0x00)
bytes.append(0x00)
bytes.append(0x00)
while True :
    ser.write(bytes)
    ack = ser.read(1).decode()
    x = ser.read(2).decode()
    ver = [int(i) for i in x]
    if (ver[0] != 0 and ver[1] != 0) :
        print("version %d.%d RF supply board firmware detected" 
            % (ver[0], ver[1]))
        break # all good
    else :
        error_count += 1
        print("*")
        time.sleep(0.250) # delay and try again

# turn off for testing purposes
print("turn off all channels")
bytes[0] = 0x50
bytes[1] = 0x00
bytes[2] = 0x00
bytes[3] = 0x00
ser.write(bytes)
ack = ser.read(1).decode()
if (ack != 'O') :
    print("\tfailed command to turn off all channels")
    error_count += 1

# configure high MPPT voltage cut off
print("Configure high MPPT cutoff as 32V")
magic_number = 32 * 19 # approx 32V
bytes[0] = 0x78 # 'x'
bytes[1] = 0
bytes[2] = (magic_number & 0xff)
bytes[3] = (magic_number >> 8)
ser.write(bytes)
ack = ser.read(1).decode()
if (ack != 'O') :
    print("\tfailed command to configure high MPPT cutoff")
    error_count += 1

# configure low MPPT voltage cut off
print("Configure low MPPT cutoff as 10V")
magic_number = 10 * 19 # approx 10V
bytes[0] = 0x6E # 'n'
bytes[1] = 0
bytes[2] = (magic_number & 0xff)
bytes[3] = (magic_number >> 8)
ser.write(bytes)
ack = ser.read(1).decode()
if (ack != 'O') :
    print("\tfailed command to configure low MPPT cutoff")
    error_count += 1

# turn on fan(s)
print("Force fans on")
bytes[0] = 0x46 # 'F'
bytes[1] = 0
bytes[2] = 1
bytes[3] = 0 
ser.write(bytes)
ack = ser.read(1).decode()
if (ack != 'O') :
    print("\tfailed command to force fans on")
    error_count += 1

# turn off fault detection for all channels
print("turn off fault detection all channels")
bytes[0] = 0x45 # 'E'
bytes[1] = 0
bytes[2] = 0
bytes[3] = 0
ser.write(bytes)
ack = ser.read(1).decode()
if (ack != 'O') :
    print("\tfailed command to turn off fault detection")
    error_count += 1

# clear all faults
print("clear all faults")
bytes[0] = 0x52 # 'R'
ser.write(bytes)
ack = ser.read(1).decode()
if (ack != 'O') :
    print("\tfailed to clear all faults")
    error_count += 1

# turn on supplies one at a time with pause
print("turn on channels one at a time")
bytes[0] = 0x50 # 'P'
bytes[1] = 0
bytes[2] = 0
bytes[3] = 1
for ch in range(1,9) :
    print(ch,end=' ',flush=True)
    bytes[1] = ch
    ser.write(bytes)
    ack = ser.read(1).decode()
    if (ack != 'O') :
        print("\n\tfailed to turn on ch ", ch)
        error_count += 1
    time.sleep(1)

print("\nRF Supply board configuration complete.")
if (error_count != 0) :
    print("\t%d errors detected" % error_count)

# for testing, wait 10 seconds then turn them off one by one
print("Waiting", end=' ', flush=True)
for i in range(0,10) :
    print(10-i, end=' ', flush=True)
    time.sleep(1)

print("turn off")
bytes[0] = 0x50
bytes[1] = 0
bytes[2] = 0
bytes[3] = 0
for ch in range(8,0,-1) :
    print(ch, end=' ', flush=True)
    bytes[1] = ch
    ser.write(bytes)
    ack = ser.read(1).decode()
    if (ack != 'O') :
        print("\n\tfailed to turn off ch ", ch)
        error_count += 1
    time.sleep(0.500)

print("\nend")
if (error_count != 0) :
    print("\t%d errors detected" % error_count)
