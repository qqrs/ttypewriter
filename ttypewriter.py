#!/usr/bin/env python
import time
import adc_spi

def main():
    DEBUG = 1

    # Raspberry PI expansion bus GPIO pins to use for SPI bus
    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25

    adc = adc_spi.ADC_SPI(SPICLK, SPIMOSI, SPIMISO, SPICS)
    adc.initadc()

    ADC_CHANNEL = 0;                # adc channel to read
    SENSOR_READ_INTERVAL = 1		# read interval in seconds

    while True:
        counts = adc.readadc(ADC_CHANNEL)

        if DEBUG:
                print "counts: %d" % counts

        time.sleep(SENSOR_READ_INTERVAL)


if __name__ == "__main__":
    main()
