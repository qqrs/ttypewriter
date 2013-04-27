#!/usr/bin/env python
import time
import adc_spi
import logging
from optparse import OptionParser

def setup():
    logging.getLogger().setLevel(logging.DEBUG)

    # Raspberry PI expansion bus GPIO pins to use for SPI bus
    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25

    adc = adc_spi.ADC_SPI(SPICLK, SPIMOSI, SPIMISO, SPICS)
    adc.initadc()
    return adc

def debug_raw_callback(option, opt, value, parser, adc, ch):
    debug_raw(adc, ch)

def debug_raw(adc, ch):
    """ Read ADC continuously and print raw read values """
    SENSOR_READ_INTERVAL = 0.1      # read interval in seconds 
                                    # max speed is ~ 300 sps
    start_time = 0
    while True:
        counts = adc.readadc(ch)
        dt = time.time() - start_time
        start_time = time.time()
        logging.debug("counts: %4d dt=%.3f" % (counts, dt))
        time.sleep(SENSOR_READ_INTERVAL)

def calibrate_callback(option, opt, value, parser, adc, ch):
    while True:
        print "keypress: %4d" % get_cal_keypress(adc, ch)

def get_cal_keypress(adc, ch):
    """ Store ADC values from key press to key release and return average """
    KEYPRESS_THRESHOLD = 5
    pressed_reads = []
    while True:
        counts = adc.readadc(ch)
        if counts > KEYPRESS_THRESHOLD:
            logging.debug("counts: %4d" % counts)
            pressed_reads.append(counts)
        elif len(pressed_reads) > 0:
            break

    avg = sum(pressed_reads)/len(pressed_reads)
    max_outlier = max([abs(x - avg) for x in pressed_reads])
    logging.info("keypress: avg=%4d max_outlier=%2d" % (avg, max_outlier))
    return avg



def main():
    ADC_CHANNEL = 0;                # adc channel to read
    adc = setup()

    parser = OptionParser()
    parser.add_option("-d", "--debugraw", action="callback", 
                callback=debug_raw_callback, callback_args=(adc,ADC_CHANNEL),
                help="print raw adc values")
    parser.add_option("-c", "--cal", action="callback", 
                callback=calibrate_callback, callback_args=(adc,ADC_CHANNEL),
                help="perform calibration")
    (options, args) = parser.parse_args()


if __name__ == "__main__":
    main()
