import asyncio
import time
import board
import keypad
import digitalio
from analogio import AnalogIn
from rainbowio import colorwheel
import neopixel
import adafruit_dht

# An array of functions tuples where 0 = detection and 1 = mapping 
state_function = [
    # 0 = Trim Potentiometer
    (lambda lightsensor, knob, pir, dht: knob.value,		        lambda x: min(max(0, x - 16371) / 49164, 1.0)),
    # 1 = Light sensor (where the reliably usable values are between 0.8 and 1.0)
    (lambda lightsensor, knob, pir, dht: lightsensor.value / 65535,	lambda x: min(max(0, (x - 0.8) * 5.0), 0.9)),
    # 2 = PIR (either motion [1] or not [0.5])
    (lambda lightsensor, knob, pir, dht: 1 if pir.value else 0,		lambda x: max(0.5, x)),
    # 3 = Humidity (percentage, mapping to blue for humid)
    (lambda lightsensor, knob, pir, dht: dht.humidity,				lambda x: min(max(0, (x - 20) * 0.015), 0.9)),
    # 4 = Temperature (in Celsius; where 10 is cold and 30 is hot)
    (lambda lightsensor, knob, pir, dht: dht.temperature,			lambda x: min(max(0, 1.0 - (((x - 10) * 0.03) + .5)), 1.0)),
]
NUM_STATES = len(state_function) - 1

# http://www.jangeox.be/2013/10/stepper-motor-28byj-48_25.html
MOTOR_FULL_ROTATION = int(4075.7728395061727 / 8)



class State:
    def __init__(self, initial_value):
        self.value = initial_value


class Stepper():
    def __init__(self, pin1, pin2, pin3, pin4, delay=0.001):
        self.mode = [
            [0, 0, 0, 1],
            [0, 0, 1, 1],
            [0, 0, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 0],
            [1, 1, 0, 0],
            [1, 0, 0, 0],
            [1, 0, 0, 1],
        ]
        self.pin1 = digitalio.DigitalInOut(pin1)
        self.pin1.direction = digitalio.Direction.OUTPUT
        self.pin2 = digitalio.DigitalInOut(pin2)
        self.pin2.direction = digitalio.Direction.OUTPUT
        self.pin3 = digitalio.DigitalInOut(pin3)
        self.pin3.direction = digitalio.Direction.OUTPUT
        self.pin4 = digitalio.DigitalInOut(pin4)
        self.pin4.direction = digitalio.Direction.OUTPUT
        self.delay = delay
        self.currentPct = 0.0
        self.reset()

    def percent(self, pct):
        adjustment = int(abs(pct - self.currentPct) * MOTOR_FULL_ROTATION)
        direction = -1 if self.currentPct - pct < 0 else 1
        self.step(adjustment, direction)
        self.currentPct = pct

    # Rotate count steps (direction -1 means backwards)
    def step(self, count, direction=1):
        for x in range(count):
            for bit in self.mode[::direction]:
                self.pin1.value = bit[0]
                self.pin2.value = bit[1]
                self.pin3.value = bit[2]
                self.pin4.value = bit[3]
                time.sleep(self.delay)
        self.reset()
        
    # Reset to 0, no holding, these are geared, you can't move them
    def reset(self):
        self.pin1.value = 0
        self.pin2.value = 0
        self.pin3.value = 0
        self.pin4.value = 0


async def setLight(state, pixel, stepper, lightsensor, knob, pir, dht):
    while True:
        (detection_func, mapping_func) = state_function[state.value]
        sensor_val = detection_func(lightsensor, knob, pir, dht)
        color_val = mapping_func(sensor_val)
        print((sensor_val, color_val))

        pixel[0] = colorwheel(color_val * 255)
        pixel.show()
        
        stepper.percent(color_val)

        # Let another task run
        await asyncio.sleep(0.2)


async def pressButton(state, pixel, stepper, btnPin):
    with keypad.Keys((btnPin,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    if state.value == NUM_STATES:
                        state.value = 0
                    else:
                        state.value += 1
                    
                    # Flash the LED for the state number
                    pixel[0] = (0, 0, 0)
                    pixel.show()
                    for i in range(state.value + 1):
                        pixel[0] = (255, 255, 255)
                        pixel.show()                        
                        time.sleep(0.15)
                        pixel[0] = (0, 0, 0)
                        pixel.show()
                        time.sleep(0.15)
                    time.sleep(0.1)

            # Let another task run
            await asyncio.sleep(0)



async def main():
    # INPUT: Light sensor
    lightsensor = AnalogIn(board.GP28_A2)

    # INPUT: Trim Potentiometer
    knob = AnalogIn(board.GP27_A1)

    # INPUT: PIR Sensor
    pir = digitalio.DigitalInOut(board.GP18)
    pir.direction = digitalio.Direction.INPUT

    # INPUT: Temperature / Humidity Sensor (DHT11)
    dht = adafruit_dht.DHT11(board.GP26_A0)
    
    # OUTPUT: Stepper Motor
    stepper = Stepper(board.GP12, board.GP13, board.GP14, board.GP15)

    # OUTPUT: Neopixel
    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=False)
    pixel[0] = (0, 0, 0)
    pixel.show()
    
    state = State(0)
    
    push_button_task = asyncio.create_task(pressButton(state, pixel, stepper, board.BUTTON))
    set_light_task = asyncio.create_task(setLight(state, pixel, stepper, lightsensor, knob, pir, dht))
    await asyncio.gather(push_button_task, set_light_task)


asyncio.run(main())
