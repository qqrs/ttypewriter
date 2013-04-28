#!/usr/bin/env python
import time
from adc_spi import ADC_SPI
import logging
from optparse import OptionParser

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


def get_cal_keypress(adc, ch):
    """ Store ADC values from key press to key release and return average """
    KEYPRESS_THRESHOLD = 5
    SENSOR_READ_INTERVAL = 0.01      # read interval in seconds 

    pressed_reads = []
    while True:
        time.sleep(SENSOR_READ_INTERVAL)
        counts = adc.readadc(ch)
        if counts > KEYPRESS_THRESHOLD:                 # key is pressed
            if len(pressed_reads) == 0:
                start_time = time.time()
            logging.debug("counts: %4d" % counts)
            pressed_reads.append(counts)
        else:                                           # no key pressed
            if len(pressed_reads) > 0:                  # key just released?
                avg = calc_keypress_avg(pressed_reads, time.time()-start_time)
                pressed_reads = []
                if avg == 0:
                    logging.debug("invalid keypress")
                else:
                    return avg


def calc_keypress_avg(reads, dt):
    """ Calculate average position of keypress if valid """
    KEYPRESS_MIN_LENGTH = 3         # min number of samples in keypress
    KEYPRESS_MIN_TIME = 0.1         # time from key press to release
    KEYPRESS_OUTLIER = 12           # max difference from median, in adc counts

    if len(reads) < KEYPRESS_MIN_LENGTH or dt < KEYPRESS_MIN_TIME:
        return 0
    med = median(reads)
    filtered_reads = [x for x in reads if abs(x-med) < KEYPRESS_OUTLIER]
    if len(filtered_reads) == 0:
        return 0

    avg = average(filtered_reads)
    max_outlier = max([abs(x - avg) for x in filtered_reads])
    logging.info("keypress: avg=%4d n=%3d nf=%3d dt=%0.4f max_outlier=%2d" % 
                    (avg, len(reads), len(filtered_reads), dt, max_outlier))
    return avg

def median(values):
    return sorted(values)[len(values)/2]
def average(values):
    return sum(values)/len(values)


def main():
    parser = OptionParser()
    parser.add_option("-d", "--debugraw", action="store_true", default=False,
                        help="print raw adc values")
    parser.add_option("-c", "--cal", action="store_true", default=False,
                        help="perform calibration")
    parser.add_option("-f", "--calfile", action="store", default="cal.dat",
                        help="calibration file to use")
    parser.add_option("-v", "--verbose", action="count", default=0,
                        dest="verbosity",
                        help="debugging verbosity v:info vv:debug")
    (opts, args) = parser.parse_args()

    if opts.verbosity > 0:
        level = logging.DEBUG if opts.verbosity > 1 else logging.INFO
        logging.getLogger().setLevel(level)

    ADC_CHANNEL = 0;            # ADC channel to read
    SPICLK = 18                 # RPI expansion bus GPIO pins to use for SPI bus
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25

    with ADC_SPI(SPICLK, SPIMOSI, SPIMISO, SPICS) as adc:
        if opts.debugraw:
            debug_raw(adc, ADC_CHANNEL)
        elif opts.cal:
            while True:
                get_cal_keypress(adc, ADC_CHANNEL)



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
