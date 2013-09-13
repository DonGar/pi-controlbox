#!/usr/bin/python

import multiprocessing
import serial
import time

class SerialProcess(multiprocessing.Process):

  def __init__(self, serial_port):
    super(SerialProcess, self).__init__()

    self._serial_port = serial_port
    self.input = multiprocessing.Queue()
    self.output = multiprocessing.Queue()

  def run(self):
    # Outer loop iterates if the serial connection is lost and reconnects.
    # This usually indicates the arduino was disconnected and reconnected.
    while True:
      try:
        with serial.Serial(self._serial_port, 115200, timeout=0.1) as s:

          while True:
            # This read will timeout if there is nothing to read.
            msg = s.readline().strip()
            if msg:
              self.output.put(msg)

            if not self.input.empty():
              msg = self.input.get()
              s.write(msg)

      except serial.SerialException:
        print 'Serial connection lost, retrying....'
        time.sleep(1)
