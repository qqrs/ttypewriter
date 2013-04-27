#!/usr/bin/env python
import time
import adc_spi
import logging

def handle_read(counts):
    if counts < 5:
	return

def main():
    logging.getLogger().setLevel(logging.DEBUG)

    # Raspberry PI expansion bus GPIO pins to use for SPI bus
    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25

    adc = adc_spi.ADC_SPI(SPICLK, SPIMOSI, SPIMISO, SPICS)
    adc.initadc()

    ADC_CHANNEL = 0;                # adc channel to read
    SENSOR_READ_INTERVAL = 0.01	    # read interval in seconds 
				    # max speed is ~ 300 sps

    start_time = 0
    while True:
        counts = adc.readadc(ADC_CHANNEL)
	handle_read(counts)
	dt = time.time() - start_time
	start_time = time.time()

	logging.debug("counts: %d dt=%f" % (counts, dt))

        time.sleep(SENSOR_READ_INTERVAL)


if __name__ == "__main__":
    main()
