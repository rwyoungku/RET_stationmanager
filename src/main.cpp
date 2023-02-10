/**********************************************************************
 * Project Name : f9t_mkrzero
 * Description  : Setup and monitor F9T GPS unit to create L1
 *                timestamps for RET
 * Sponsor      : S. prohira
 * Device       : MKR Zero
 * Compiler     : platformIO Core 6.1.6
 *              : Visual Studio Code 1.74.3
 * Module name  :
 * Last Revised :
 *
 * Instrumentation Design Laboratory
 * Malott Hall, Room 6042
 * 1251 Wescoe Hall Drive, The University of Kansas
 * Lawrence, Kansas 66045
 *
 * Robert W. Young, Director, Design Engineer
 *
 * Notes        : RET needs to time stamp the L1 triggers with some
 *                degree of accuracy. Using the L1 signal from the
 *                ZCU111 as an interrupt input to the F9T module it
 *                will latch the latest contents of the TIM_TIM2
 *                data structure.
 *                The MKRZero talks to the Station Manager (rPi4) via
 *                UART1. If the MKRZero receives a 'G' then it will
 *                return either the latest time latched or a string
 *                beginning with -1 to indicate no time has been
 *                latched.
 *
 *                Error message are sent out on USB serial
 *
 *                Needs watchdog
 **********************************************************************/
#include "f9t_mkrzero.h"

/**********************************************************************
   void setup()
   Purpose   : Configure all the Arduino things
   Arguments : none
   Returns   : none
   Calls     : various
   Notes     :
   Tested    : 02-2023
 *********************************************************************/
void setup()
{
  Serial.begin(115200);
  Serial1.begin(115200);

  Wire.begin();

  watchdog_setup();

  if (myGNSS.begin() == false) // Connect to the u-blox module using Wire port
  {
    Serial.println(F("u-blox GNSS not detected at default I2C address. Please check wiring. Freezing."));
    while (1)
    {
      Serial.println("u-blox GNSS init error");
      delay(500);
    }
  }
  watchdog_clear();
  myGNSS.setI2COutput(COM_TYPE_UBX);                 // Set the I2C port to output UBX only (turn off NMEA noise)
  myGNSS.saveConfigSelective(VAL_CFG_SUBSEC_IOPORT); // Save (only) the communications port settings to flash and BBR
  myGNSS.setNavigationFrequency(1);                  // Produce one solution per second
  myGNSS.setAutoTIMTM2callbackPtr(&latchTIMTM2data); // Enable automatic TIM TM2 messages with callback to printTIMTM2data
  watchdog_clear();

  Serial.println("Compete");
}

/**********************************************************************
   void loop()
   Purpose   : Main execution loop. Dispatch all from here
   Arguments : none
   Returns   : none
   Calls     : various
   Notes     :
   Tested    :
 *********************************************************************/
void loop()
{
  myGNSS.checkUblox();     // Check for the arrival of new data and process it.
  myGNSS.checkCallbacks(); // Check if any callbacks are waiting to be processed.

  if (Serial1.available() > 0)
  {
    if (Serial1.read() == 'G')
    {
      // we've been asked for GPS data
      if (fresh_time_data == 1)
      {
        // there is un-read latest latched gps time
        Serial1.print(latest_data.count);
        Serial1.write(' ');
        Serial1.print(latest_data.wnR);
        Serial1.write(' ');
        Serial1.print(latest_data.towMsR);
        Serial1.write(' ');
        Serial1.print(latest_data.towSubMsR);
        Serial1.write(' ');
        Serial1.println(latest_data.accEst);
        fresh_time_data = 0;
      }
      else
      {
        Serial1.println("-1 0 0 0 0"); // nothing new to report
        SIV = myGNSS.getSIV();
        Serial.println(SIV); // report the sattellites in view 
      }
    }
  }
  watchdog_clear();
}

/**********************************************************************
   void latchTIMTM2data(UBX_TIM_TM2_data_t *ubxDataStruct)
   Purpose   : Callback to latch the latest time in GPS
   Arguments : none
   Returns   : none
   Calls     : various
   Notes     :
   Tested    :
 *********************************************************************/
void latchTIMTM2data(UBX_TIM_TM2_data_t *ubxDataStruct)
{
  latest_data = *ubxDataStruct;

  fresh_time_data = 1;
}

void watchdog_setup(void)
{
  // Set up the generic clock (GCLK2) used to clock the watchdog timer at 1.024kHz
  REG_GCLK_GENDIV = GCLK_GENDIV_DIV(4) | // Divide the 32.768kHz clock source by divisor 32, where 2^(4 + 1): 32.768kHz/32=1.024kHz
                    GCLK_GENDIV_ID(2);   // Select Generic Clock (GCLK) 2
  while (GCLK->STATUS.bit.SYNCBUSY)
    ; // Wait for synchronization

  REG_GCLK_GENCTRL = GCLK_GENCTRL_DIVSEL |        // Set to divide by 2^(GCLK_GENDIV_DIV(4) + 1)
                     GCLK_GENCTRL_IDC |           // Set the duty cycle to 50/50 HIGH/LOW
                     GCLK_GENCTRL_GENEN |         // Enable GCLK2
                     GCLK_GENCTRL_SRC_OSCULP32K | // Set the clock source to the ultra low power oscillator (OSCULP32K)
                     GCLK_GENCTRL_ID(2);          // Select GCLK2
  while (GCLK->STATUS.bit.SYNCBUSY)
    ; // Wait for synchronization

  // Feed GCLK2 to WDT (Watchdog Timer)
  REG_GCLK_CLKCTRL = GCLK_CLKCTRL_CLKEN |     // Enable GCLK2 to the WDT
                     GCLK_CLKCTRL_GEN_GCLK2 | // Select GCLK2
                     GCLK_CLKCTRL_ID_WDT;     // Feed the GCLK2 to the WDT
  while (GCLK->STATUS.bit.SYNCBUSY)
    ; // Wait for synchronization

  REG_WDT_CONFIG = WDT_CONFIG_PER_11; // Set the WDT reset timeout to 16 seconds
  while (WDT->STATUS.bit.SYNCBUSY)
    ;                             // Wait for synchronization
  REG_WDT_CTRL = WDT_CTRL_ENABLE; // Enable the WDT in normal mode
  while (WDT->STATUS.bit.SYNCBUSY)
    ; // Wait for synchronization
}

void watchdog_clear(void)
{
  if (!WDT->STATUS.bit.SYNCBUSY) // Check if the WDT registers are synchronized
  {
    REG_WDT_CLEAR = WDT_CLEAR_CLEAR_KEY; // Clear the watchdog timer
  }
}