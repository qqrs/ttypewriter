#!/usr/bin/env python

import os
import sys
import time
import string
import logging
import pickle
from bisect import bisect_left
from optparse import OptionParser
from adc_spi import ADC_SPI

def debug_raw(adc, ch):
    """ Read ADC continuously and print raw values """
    SENSOR_READ_INTERVAL = 0.1      # read interval in seconds 
                                    # max speed is ~ 300 sps
    start_time = 0
    while True:
        counts = adc.readadc(ch)
        dt = time.time() - start_time
        start_time = time.time()
        logging.debug("counts: %4d dt=%.3f" % (counts, dt))
        time.sleep(SENSOR_READ_INTERVAL)

# TODO: support sequential presses without a full release between them
def typewriter(adc, ch, calfile, screen_session):
    """ Load calibration and decode typewriter keypresses to stdout """
    (keycodes, seps) = load_calfile(calfile)
    while True:
        code = get_cal_keypress(adc, ch)
        key = lookup_key(keycodes, seps, code)
        if screen_session is None:
            # print keypress to stdout
            sys.stdout.write(key)
            sys.stdout.flush()
        else:
            # send keypress to a screen session
            rc = os.system("screen -S %s -X stuff '%s' > /dev/null" 
                        % (screen_session, key))
            if rc != 0:
                raise EnvironmentError(
                        "Screen session '%s' not found" % screen_session)

def lookup_key(keycodes, seps, code):
    """ Find key for keycode by binary search """
    ADC_MIN = 0
    ADC_MAX = 1023
    if code < ADC_MIN or code > ADC_MAX:
        raise ValueError("Key code out of range")
    i = bisect_left(seps, code)
    return keycodes[i][1]

# TODO: check for empty file
def load_calfile(calfile):
    """ Load calibration from file and calculate separators between keys """
    with open(calfile, "r") as f:
        keycodes = pickle.load(f)
    keycodes.sort(key=lambda (code,key): code)
    seps = calc_seppoints(keycodes)
    return (keycodes, seps)

def calc_seppoints(keycodes):
    """ Calculate separation point between keycodes: int avg of adjacent pts """
    it_left = iter(keycodes)
    it_right = iter(keycodes)
    it_right.next()
    seps = [(x+y)/2 for ((x,key),(y,_)) in zip(it_left, it_right)]
    assert(len(seps) == len(keycodes) - 1)
    return seps

# TODO: read each key multiple times and check for consensus
# TODO: check for multiple keys using the same keycode
def calibrate(adc, ch, calfile):
    """ Calibrate and store to calfile """
    keys = string.ascii_lowercase + string.digits + "-!:@,./" # typewriter keys
    keys = keys.translate(None, "q1")       # remove keys that don't exist
    keycodes = []
    for key in keys:
        print "Press key %s" % key
        code = get_cal_keypress(adc, ch)
        keycodes.append((code, key))
        print "Got key %s: %4d" % (key, code)
        print
    with open(calfile, "w") as f:
        pickle.dump(keycodes, f)

def get_cal_keypress(adc, ch):
    """ Wait for press -- return avg ADC value from key press to key release """
    KEYPRESS_THRESHOLD = 5       # ADC read <= threshold mean all keys released 
    SENSOR_READ_INTERVAL = 0.01  # ADC sample delay in seconds 

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
            if len(pressed_reads) > 0:                  # key was just released
                avg = calc_keypress_avg(pressed_reads, time.time()-start_time)
                pressed_reads = []
                if avg == 0:
                    logging.debug("invalid keypress")
                else:
                    return avg


def calc_keypress_avg(reads, dt):
    """ Check that keypress is valid and calculate keycode as average position. 
        Return 0 if not a valid key press. """
    KEYPRESS_MIN_LENGTH = 3         # min number of samples in keypress
    KEYPRESS_MIN_TIME = 0.1         # time from key press to release
    KEYPRESS_OUTLIER = 12           # max difference from median, in adc counts

    if len(reads) < KEYPRESS_MIN_LENGTH or dt < KEYPRESS_MIN_TIME:
        return 0
    med = median(reads)

    # filter outliers with respect to median value
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
    parser.add_option("-S", "--session", action="store", default=None,
                        help="screen session to receive keypresses")
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
            calibrate(adc, ADC_CHANNEL, opts.calfile)
        else:
            typewriter(adc, ADC_CHANNEL, opts.calfile, opts.session)



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
