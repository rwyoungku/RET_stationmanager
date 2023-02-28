"""Place 8-bit value on output of 74x595 register

The 74HC595 register on the RET Station Manager board is used to
turn off or on the +12V and +24V power supplies on the Station
Manager Power Supply Board

syntax:
shift ABCDEFGH 
    ABCDEFGH represent the outputs of the 74HC595
    Bit A controls the +12V power supply (RALF, etc.)
    Bit B controls the +24V power supply (SURF, etc.)
    All other bits ignored.
    A 1 turns on the supply, a 0 turns off the supply.

sample
python shift 11000000
    turn on both power supplies

RET Station Manager support code
Tested Feb 27, 2023 RWY

"""

import RPi.GPIO as GPIO
import sys

# use BCM numbering
dataPIN = 10
latchPIN = 17
clockPIN = 11

GPIO.setwarnings(False) # shhhhhh
GPIO.setmode(GPIO.BCM) 
GPIO.setup((dataPIN, latchPIN, clockPIN), GPIO.OUT)


def shift_update(input,data,clock,latch):
    #put latch down to start data sending
    GPIO.output(clock,0)
    GPIO.output(latch,0)
    GPIO.output(clock,1)

    #load data in reverse order
    for i in range(7, -1, -1):
        GPIO.output(clock,0)
        GPIO.output(data, int(input[i]))
        GPIO.output(clock,1)

    #put latch up to store data on register
    GPIO.output(clock,0)
    GPIO.output(latch,1)
    GPIO.output(clock,1)

shift_update(sys.argv[1], dataPIN, clockPIN, latchPIN)

GPIO.cleanup()

