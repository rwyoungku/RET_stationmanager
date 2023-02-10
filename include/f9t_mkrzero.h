#include <Arduino.h>

#include <Wire.h> //Needed for I2C to GPS

#include <SparkFun_u-blox_GNSS_v3.h> //http://librarymanager/All#SparkFun_u-blox_GNSS_v3

// Each cycle is about 1mS.
#define WDT_CONFIG_PER_3    0x3u    // 64 clock cycles
#define WDT_CONFIG_PER_4    0x4u    // 128 clock cycles
#define WDT_CONFIG_PER_5    0x5u    // 256 clock cycles
#define WDT_CONFIG_PER_6    0x6u    // 512 clock cycles
#define WDT_CONFIG_PER_7    0x7u    // 1024 clock cycles
#define WDT_CONFIG_PER_8    0x8u    // 2048 clock cycles
#define WDT_CONFIG_PER_9    0x9u    // 4096 clock cycles
#define WDT_CONFIG_PER_10   0xAu    // 8192 clock cycles
#define WDT_CONFIG_PER_11   0xBu    // 16384 clock cycles

SFE_UBLOX_GNSS myGNSS;
UBX_TIM_TM2_data_t latest_data;

int fresh_time_data = 0;
int SIV;



void watchdog_setup(void);
void watchdog_clear(void);
void latchTIMTM2data(UBX_TIM_TM2_data_t *ubxDataStruct);