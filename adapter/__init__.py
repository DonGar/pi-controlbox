
import multiprocessing

class ConnectionBase(multiprocessing.Process):
  """This class performs IO in a different process to avoid blocking.

  It uses a multiprocessing.Connection to communicate back to the main loop
  since that object provides a FD compatible with select calls.
  """
  def __init__(self):
    super(ConnectionBase, self).__init__()
    a, b = multiprocessing.Pipe()

    # Connection for the control process to use.
    self.connection = a

    # Connection for the local process to use.
    self._connection = b

  def run(self):
    assert False, "Not implemented."
