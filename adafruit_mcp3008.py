#!/usr/bin/env python
import time
import urllib
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

SENSOR_ID = "upstairs-wc"
SERVER_UPDATE_URL = "https://hswc.herokuapp.com/update"
def update_server_state(state):
	global SENSOR_ID
	global SERVER_UPDATE_URL

	sensor_val = "1" if state else "0"

	params = {}
	params['sensor_id'] = SENSOR_ID
	params['sensor_val'] = sensor_val
	params = urllib.urlencode(params)

	try:
		f = urllib.urlopen(SERVER_UPDATE_URL, params)
	except IOError as e:
		if DEBUG:
			print "I/O error %s: %s" % (e.errno, e.strerror)
			print "Connection error on HTTP POST to %s" % SERVER_UPDATE_URL
		return False

	return f.getcode() == 200


# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# 10k trim pot connected to adc #0
potentiometer_adc = 0;

SENSOR_ACTIVE_THRESHOLD = 700		# threshold in ADC counts
SENSOR_READ_INTERVAL = 1		# interval in seconds
MAX_SERVER_UPDATE_INTERVAL = 60		# interval in seconds
FILTER_SAMPLES = 5			# samples to average

sensor_hist = list()     # this keeps track of the last potentiometer value
last_state = None
last_update_time = 0

while True:
        # read the analog pin
        sensor_counts = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
	if len(sensor_hist) > FILTER_SAMPLES:
		del sensor_hist[0]
        sensor_hist.append(sensor_counts)

	sensor_avg = sum(sensor_hist)/len(sensor_hist)
	sensor_state = sensor_avg > SENSOR_ACTIVE_THRESHOLD

        if DEBUG:
                print ("sensor_counts:", sensor_counts, 
			" sensor_avg:", sensor_avg, 
			" sensor_state: ", sensor_state)


	if (sensor_state != last_state
			or int(time.time()) - last_update_time > MAX_SERVER_UPDATE_INTERVAL):
		if update_server_state(sensor_state):
			last_update_time = int(time.time())	# update was successful
			last_state = sensor_state

        # hang out and do nothing for a half second
        time.sleep(SENSOR_READ_INTERVAL)
