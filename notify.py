#!/usr/bin/python

import urllib
import multiprocessing

def _url_notify_helper(url):
  f = urllib.urlopen(url)
  f.read()
  f.close()

class Notifier:
  def __init__(self):
    self.pool = multiprocessing.Pool(5)

  def notify_url(self, url):
    self.pool.apply_async(_url_notify_helper, (url,))
