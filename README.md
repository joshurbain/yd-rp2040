# yd-rp2040
Labs and course materials for Microcontroller Mastery, a class based on the Raspberry Pi Pico (using YD-RP2040 from VCC-GND.com)

All of the labs can use the Adafruit CircuitPython boot image, however, to use Piper Make (https://make.playpiper.com/) you will likely need to change your boot image using the "Setup My Pico" functionality on their site.

**NOTE:** All of the libraries needed for the projects are in the lib/ folder. Almost all of them have been cross-compiled to the architecture for the YD-RP2040 for speed. Instructions for this process are described in the [CircuitPython documentations](https://learn.adafruit.com/welcome-to-circuitpython/library-file-types-and-frozen-libraries).

---

## Project requirements
- VCC-GND Raspberry Pi Pico (YD-RP2040) 16MB Board USB-C with RGB LED and User Button
- Medium-sized (or larger) solderless breadboard
- Battery Pack (optional if using USB-C power; 8x AA with switch recommended)
- LM7805 Voltage Regulator (optional if using USB-C power)
- Boardboard and 6-10 Jumper Wires
- Stepper Motor and 5V 28BYJ-48 Motor Driver
- DHT11 Humidity and Temperature Sensor
- PIR Motion Sensor
- 3x LEDs (preferably red, yellow, and green)
- 3x 470 Ohm Resistor
- 1x 10K Ohm Resistor
- 160 Ohm Passive Electronic Buzzer
- 10K Ohm Trim Potentiometer with Knob
- 6x6x5mm Micro Momentary Tactile Switch
- LDR Photo-resistor Light Sensor Photocell

---

## Other content to consider
### Websites
- Piper Make (https://make.playpiper.com/)
- CircuitPython (https://circuitpython.org/board/vcc_gnd_yd_rp2040/)
- David Haworth (WA9ONY)'s amazing GitHub (https://github.com/WA9ONY/Pico-RP2040)
### Books
- Get started with MicroPython Raspberry Pi Pico by Raspberry Pi Press (ISBN 978-1-912047-29-1 or on Amazon at https://a.co/d/8mpaz0i) which is written for the Raspberry Pi Pico RP2040W (wireless model), but all the [non-wireless] concepts apply to this board as well.
