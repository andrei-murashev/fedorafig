# System imports
import os
import logging
import traceback

# Local imports
import help


"""When raising this exception, this utility will exit gracefully and display
any error info to the user."""
class FedorafigException(Exception):
  def __init__(self, msg, *pargs, args=None, exc=None):
    print("FedorafigException raised", flush=True)
    if exc is None:
      super().__init__(msg);
    else:
      print(msg)
      if isinstance(exc, SystemExit): traceback.print_exception(
        type(exc), exc, exc.__traceback__)
      else: raise exc


  @staticmethod
  def format(args, exc):
    pass



LOG = None
def log(exc):
  global LOG
  from cfg import STATE_DIR
  if LOG is None: LOG = os.path.join(STATE_DIR, 'log.txt')

  logging.basicConfig(
    filename=LOG,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
  )

  logging.error(str(exc), exc_info=exc)
  print('fedorafig:', "Unknown error:", str(exc))
