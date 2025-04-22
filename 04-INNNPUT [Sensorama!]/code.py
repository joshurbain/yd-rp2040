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
    # 0 = Light sensor (where the reliably usable values are between 0.8 and 1.0)
    (lambda analog_in, pir, dht: analog_in.value / 65535,	lambda x: min(max(0, (x - 0.8) * 5.0), 0.9)),
    # 1 = PIR (either motion [1] or not [0.5])
    (lambda analog_in, pir, dht: 1 if pir.value else 0,		lambda x: max(0.5, x)),
    # 2 = Humidity (percentage, mapping to blue for humid)
    (lambda analog_in, pir, dht: dht.humidity,				lambda x: min(max(0, (x - 20) * 0.015), 0.9)),
    # 3 = Temperature (in Celsius; where 10 is cold and 30 is hot)
    (lambda analog_in, pir, dht: dht.temperature,			lambda x: min(max(0, 1.0 - (((x - 10) * 0.03) + .5)), 1.0)),
]
NUM_STATES = len(state_function) - 1



class State:
    def __init__(self, initial_value):
        self.value = initial_value


async def setLight(state, pixel, analog_in, pir, dht
):
    while True:
        (detection_func, mapping_func) = state_function[state.value]
        sensor_val = detection_func(analog_in, pir, dht)
        color_val = mapping_func(sensor_val)
        print((sensor_val, color_val))

        pixel[0] = colorwheel(color_val * 255)
        pixel.show()

        # Let another task run
        await asyncio.sleep(0.2)


async def pressButton(state, pixel, btnPin):
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
    # Light sensor
    analog_in = AnalogIn(board.GP28_A2)

    # PIR Sensor
    pir = digitalio.DigitalInOut(board.GP18)
    pir.direction = digitalio.Direction.INPUT

    # Temperature / Humidity Sensor (DHT11)
    dht = adafruit_dht.DHT11(board.GP26_A0)

    # Neopixel
    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=False)
    pixel[0] = (0, 0, 0)
    pixel.show()
    
    state = State(0)
    
    push_button_task = asyncio.create_task(pressButton(state, pixel, board.BUTTON))
    set_light_task = asyncio.create_task(setLight(state, pixel, analog_in, pir, dht))
    await asyncio.gather(push_button_task, set_light_task)


asyncio.run(main())
