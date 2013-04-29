This project interfaces a mechanical typewriter to a Raspberry Pi. See the project on my [blog](/TODO).

adc_spi.py:
Microchip MCP3008 analog-to-digital converter interface. Bit-bangs SPI on Raspberry Pi GPIO pins. Based on code from [Adafruit](http://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/overview).

ttypewriter.py:
Decode typewriter key presses and write characters to stdout.

```
Usage: ttypewriter.py [options]

Options:
  -h, --help            show this help message and exit
  -d, --debugraw        print raw adc values
  -c, --cal             perform calibration
  -f CALFILE, --calfile=CALFILE
                        calibration file to use
  -v, --verbose         debugging verbosity v:info vv:debug
```
