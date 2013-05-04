This project interfaces a mechanical typewriter to a Raspberry Pi using a SoftPot touch sensor. 

*adc_spi.py*:
Microchip MCP3008 analog-to-digital converter interface. Bit-bangs SPI on Raspberry Pi GPIO pins. Based on code from [Adafruit](http://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/overview).

*ttypewriter.py*:
Typewriter calibration and keypress decoding.

Run `sudo python ttypewriter.py -c` and press each key when prompted to create the calibration file.  
Run `sudo python ttypewriter.py` to decode keypresses and write characters to stdout.  
Open a screen session with `sudo screen -S <session_name>` and run `sudo python ttypewriter.py -S <session_name>` to decode keypresses and inject characters into the screen session.  


```
Usage: ttypewriter.py [options]

Options:
  -h, --help            show this help message and exit
  -d, --debugraw        print raw adc values
  -c, --cal             perform calibration
  -f CALFILE, --calfile=CALFILE
                        calibration file to use
  -S SESSION, --session=SESSION
                        screen session to receive keypresses
  -v, --verbose         debugging verbosity v:info vv:debug
```
