import asyncio
import time
import board
import keypad
import pwmio
from piper_blockly import *

## ---- Definitions ---- ##
v = None

try:
  set_digital_view(True)
except:
  pass


class State:
    def __init__(self, initial_value):
        self.value = initial_value

async def streetlight(state, lightRed, lightYellow, lightGreen, neopixel):
  waitGreen = 8
  waitYellow = 3
  waitRed = 5
  while True:
    # print("R %d, Y %d, G %d" % (waitRed, waitYellow, waitGreen))
    
    # Green light
    state.value = 2
    lightGreen.setPin(1)
    await asyncio.sleep(waitGreen)
    lightGreen.setPin(0)

    # Yellow light
    state.value = 1
    lightYellow.setPin(1)
    await asyncio.sleep(waitYellow)
    lightYellow.setPin(0)

    # Red light
    state.value = 0
    lightRed.setPin(1)
    await asyncio.sleep(waitRed)
    lightRed.setPin(0)

    waitGreen = random.random() * 5
    waitYellow = random.random() * 3
    waitRed = random.random() * 10


async def catch_interrupt(state, pin, buzzer):
  with keypad.Keys((pin,), value_when_pressed=False) as keys:
    while True:
      event = keys.events.get()
      if event:
          if event.pressed:
            if state.value == 2:
                buzzer.frequency = 523
            elif state.value == 1:
                buzzer.frequency = 440
            else:
                buzzer.frequency = 262

            buzzer.duty_cycle = 65535 // 2 # 50%
            time.sleep(0.1)
            buzzer.duty_cycle = 0 # Off

      # Let another task run
      await asyncio.sleep(0)


async def main():
  buzzer = pwmio.PWMOut(board.GP16, frequency=440, duty_cycle=0, variable_frequency=True)
  
  lightRed = piperPin(board.GP26, "GP26")
  lightRed.setPin(0)
  lightYellow = piperPin(board.GP27, "GP27")
  lightYellow.setPin(0)
  lightGreen = piperPin(board.GP28, "GP28")
  lightGreen.setPin(0)
  neopixel = piperNeoPixels(board.GP23, "GP23", 1)
  neopixel.fill((0, 0, 0))
  neopixel.show()

  state = State(0) # 0 = Red, 1 = Yellow, 2 = Green

  interrupt_task = asyncio.create_task(catch_interrupt(state, board.BUTTON, buzzer))
  streetlight_task = asyncio.create_task(streetlight(state, lightRed, lightYellow, lightGreen, neopixel))
  await asyncio.gather(interrupt_task, streetlight_task)

asyncio.run(main())
