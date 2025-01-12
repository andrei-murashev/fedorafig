# TODO: Figure out why I'm still getting huge error messages
# TODO: Still need to get these to work properly
from typing import *

def fedorafig_exc(msg: str, *args: str,
  exc: Optional[BaseException] = None) -> None:
  print('fedorafig:', msg, *args)
  if exc is not None: print("Accompanying error:", str(exc))
  exit(2)


def log_exc(exc: BaseException) -> None:
  import logging; from cmn import LOG_FILE
  logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
  )

  logging.error(str(exc), exc_info=exc)
  print("fedorafig:", "Unforeseen error logged:")
  print(str(exc))
  exit(1)
