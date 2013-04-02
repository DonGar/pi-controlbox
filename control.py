#!/usr/bin/python

import time
import urllib

import RPi.GPIO as GPIO

BUTTON_URL = {
  7: 'http://www:8080/button?id=system1',
  11: 'http://www:8080/button?id=system2',
  13: 'http://www:8080/button?id=system3',
  15: 'http://www:8080/button?id=system4',
  8: 'http://www:8080/button?id=doorbell',
}

BUTTON_PINS = BUTTON_URL.keys()
BUTTON_LIGHT = {7: 10, 11: 16, 13: 18, 15: 22}
LIGHT_PINS = BUTTON_LIGHT.values()

BUTTON_DOWN = {}
LIGHT_ON = {10: False, 11: False, 18: False, 22: False}

def button_pushed(pin):
  print 'Button down!: %d' % pin

  on_off = ''

  if pin in BUTTON_LIGHT:
    light_pin = BUTTON_LIGHT[pin]

    # Request a change to the oposite of the current state.
    if light_pin:
      on_off = '&action=off'
    else:
      on_off = '&action=on'

    # Notice that GPIO setting is False for light, True for dark.
    gpio_setting = LIGHT_ON[light_pin]
    GPIO.output(light_pin, gpio_setting)
    LIGHT_ON[light_pin] = not gpio_setting

  url = BUTTON_URL[pin] + on_off
  f = urllib.urlopen(url)
  f.read()
  f.close()

def main():
  GPIO.setmode(GPIO.BOARD)
  GPIO.setwarnings(False)

  for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN)

  for pin in LIGHT_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, True)
    LIGHT_ON[pin] = False

  while True:
    # If the pin transitioned to low since we checked, it's been pushed.
    for pin in BUTTON_PINS:

      read_down = GPIO.input(pin)

      if read_down != BUTTON_DOWN.get(pin, False):
        BUTTON_DOWN[pin] = read_down

        if read_down:
          button_pushed(pin)

    time.sleep(0.05)

if __name__ == "__main__":
    main()
