import RPi.GPIO as GPIO

class ADC_SPI(object):
    def __init__(self, clockpin, mosipin, misopin, cspin):
        self.clockpin = clockpin
        self.mosipin  = mosipin
        self.misopin  = misopin
        self.cspin    = cspin  

    def __enter__(self):
        self.initadc()

    def __exit__(self):
        self.cleanup()

    def initadc(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.mosipin, GPIO.OUT)
        GPIO.setup(self.misopin, GPIO.IN)
        GPIO.setup(self.clockpin, GPIO.OUT)
        GPIO.setup(self.cspin, GPIO.OUT)

    def cleanup(self):
        GPIO.cleanup()

    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def readadc(self, adcnum):
            if ((adcnum > 7) or (adcnum < 0)):
                    return -1
            GPIO.output(self.cspin, True)

            GPIO.output(self.clockpin, False)  # start clock low
            GPIO.output(self.cspin, False)     # bring CS low

            commandout = adcnum
            commandout |= 0x18  # start bit + single-ended bit
            commandout <<= 3    # we only need to send 5 bits here
            for i in range(5):
                    if (commandout & 0x80):
                            GPIO.output(self.mosipin, True)
                    else:
                            GPIO.output(self.mosipin, False)
                    commandout <<= 1
                    GPIO.output(self.clockpin, True)
                    GPIO.output(self.clockpin, False)

            adcout = 0
            # read in one empty bit, one null bit and 10 ADC bits
            for i in range(12):
                    GPIO.output(self.clockpin, True)
                    GPIO.output(self.clockpin, False)
                    adcout <<= 1
                    if (GPIO.input(self.misopin)):
                            adcout |= 0x1

            GPIO.output(self.cspin, True)
            
            adcout >>= 1       # first bit is 'null' so drop it
            return adcout

def demoadc():
    import time
    DEBUG = 1

    # Raspberry PI expansion bus GPIO pins to use for SPI bus
    SPICLK = 18
    SPIMISO = 23
    SPIMOSI = 24
    SPICS = 25

    adc = ADC_SPI(SPICLK, SPIMOSI, SPIMISO, SPICS)
    adc.initadc()

    ADC_CHANNEL = 0;                # adc channel to read
    SENSOR_READ_INTERVAL = 1		# read interval in seconds

    while True:
        counts = adc.readadc(ADC_CHANNEL)

        if DEBUG:
                print "counts: %d" % counts

        time.sleep(SENSOR_READ_INTERVAL)


if __name__ == "__main__":
    demoadc()
