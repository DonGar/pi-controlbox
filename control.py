#!/usr/bin/python

import json
import os
import time

import adapter
import serial_process

# import RPi.GPIO as GPIO

SERIAL_PORT = '/dev/ttyUSB0'
SERVER_URL = 'http://www:8080/'
ADAPTER_URL = os.path.join(SERVER_URL, 'status/control')

BUTTONS = ('block_2',
           'block_1',
           'block_4',
           'block_3',
           'desktop_doorbell',
           'black',
           'red')

RGBS = ('block_2_backlight',
        'block_1_backlight',
        'block_4_backlight',
        'block_3_backlight')

def serial_colors_in_to_adapter_colors(colors):
  """[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]] ->
  { "block_1_backlight": [0, 0, 0],
    "block_2_backlight": [0, 0, 0],
    "block_3_backlight": [0, 0, 0],
    "block_4_backlight": [0, 0, 0] }
  """
  return dict((rgb, color) for rgb, color in zip(RGBS, colors))

def adapter_colors_to_serial_colors_out(colors):
  """
  { "block_1_backlight": [0, 0, 0],
    "block_2_backlight": [0, 0, 0],
    "block_3_backlight": [0, 0, 0],
    "block_4_backlight": [0, 0, 0] } ->
  '000:000:000:000'
  """
  result = ':'.join(['%d%d%d' % tuple(colors[rgb]) for rgb in RGBS])
  return result

def main():
  # All buttons initialize to unpushed, and all colors to black.
  button_state = [False] * len(BUTTONS)
  color_state = serial_colors_in_to_adapter_colors([[0, 0, 0]] * len(RGBS))
  targets = {}
  targets.update(color_state)

  # Setup the serial port process.
  serial = serial_process.SerialProcess(SERIAL_PORT)
  serial.start()

  # Start up the web adapter writer.
  web_updater = adapter.WebAdapterUpdater(SERVER_URL, ADAPTER_URL,
                                          BUTTONS, RGBS)

  # Reset the web adapter to known state.
  web_updater.setup_adapter(color_state)

  # Start up the web adapter reader (only after the reset).
  web_watcher = adapter.WebAdapterWatcher(ADAPTER_URL)
  web_watcher.start()

  # I would love to have a way to select between the multiple queues.
  # Instead this code polls each one.
  while True:
    if not serial.output.empty():
      # { "buttons": [0, 0, 0, 0, 0, 0, 0],
      #   "colors": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]] }
      msg = json.loads(serial.output.get())

      # Handle Button Changes
      updated_buttons = msg['buttons']
      for b in xrange(len(msg['buttons'])):
        if updated_buttons[b] and updated_buttons[b] != button_state[b]:
          print 'Button %s pushed.' % BUTTONS[b]
          web_updater.push_button(BUTTONS[b])
      button_state = updated_buttons

      new_colors = serial_colors_in_to_adapter_colors(msg['colors'])
      if color_state != new_colors:
        color_state = new_colors
        print 'New colors %s' % color_state
        web_updater.update_colors(color_state)

    if not web_watcher.output.empty():
      msg = web_watcher.output.get()
      print 'Web updated: %s' % msg

      if msg['status'] == {}:
        web_updater.setup_adapter(color_state)
        continue

      # Look for requests to update background colors that don't match
      # current colors.
      targets.update(msg['status']['rgb_target'])

    # If our displayed colors don't match our target colors, request a color
    # update.
    if targets != color_state:
      print 'Updating colors: %s' % targets
      serial.input.put(adapter_colors_to_serial_colors_out(targets))

    time.sleep(0.01)

if __name__ == "__main__":
  main()
