#!/usr/bin/python

import multiprocessing
import json
import os
import requests
import time


class WebAdapterWatcher(multiprocessing.Process):

  def __init__(self, url):
    super(WebAdapterWatcher, self).__init__()

    self.url = url
    self.output = multiprocessing.Queue()

  def run(self):
    revision = None

    while True:
      try:
        r = requests.get(self.url, params={'revision': revision})
        if r:
          rj = r.json()
          revision = rj['revision']
          self.output.put(rj)

      except requests.exceptions:
        # If we got an error back from the server, wait a bit and try again.
        time.sleep(0.5)

class WebAdapterUpdater(object):

  def __init__(self, server_url, adapter_url, buttons, rgbs):
    self.server_url = server_url
    self.adapter_url = adapter_url
    self.buttons = buttons
    self.rgbs = rgbs

    self.pool = multiprocessing.Pool(5)

  def setup_adapter(self, colors):

    template = {}

    # Add the buttons to the adapter template.
    template['button'] = {}
    for button in self.buttons:
      template['button'][button] = {}

    # Add RGB light status and request fields.
    template['rgb'] = colors
    template['rgb_target'] = {}

    json_template = json.dumps(template)

    print 'New Adapter: %s' % json_template

    headers = {'content-type': 'application/json'}
    requests.put(self.adapter_url, data=json_template, headers=headers)

  def update_colors(self, colors):
    url = os.path.join(self.adapter_url, 'rgb')
    headers = {'content-type': 'application/json'}
    self.pool.apply_async(requests.put,
                          (url,),
                          {'data': json.dumps(colors), 'headers': headers})


  def push_button(self, button):
    url = os.path.join(self.server_url, 'button', button)
    self.pool.apply_async(requests.get, (url,))
