#!/usr/bin/python

import time

import RPi.GPIO as GPIO

import notify

BUTTON_URL = {
  7: 'http://www:8080/button?id=control_red',
  11: 'http://www:8080/button?id=control_black',
  8: 'http://www:8080/button?id=doorbell',
}

BUTTON_PINS = BUTTON_URL.keys()
BUTTON_DOWN = {}

notifier = notify.Notifier()


def check_buttons():
  # If the pin transitioned to low since we checked, it's been pushed.
  for pin in BUTTON_PINS:

    read_down = GPIO.input(pin)

    # Pin 7 is normally high, transitions to low when pushed.
    if pin == 7:
      read_down = not read_down

    if read_down != BUTTON_DOWN.get(pin, False):
      BUTTON_DOWN[pin] = read_down

      if read_down:
        print 'Button down!: %d' % pin
        notifier.notify_url(BUTTON_URL[pin])


def main():
  GPIO.setmode(GPIO.BOARD)
  GPIO.setwarnings(False)

  for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN)

  while True:
    check_buttons()
    time.sleep(0.05)

if __name__ == "__main__":
  main()
