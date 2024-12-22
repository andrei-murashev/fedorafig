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
      print(f"fedorafig: {msg}:", *pargs)
    else:
      print(f"Python error: {exc}")
      print(f"fedorafig: {msg}:", *pargs)


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
