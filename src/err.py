# TODO: Figure out why I'm still getting huge error messages
# TODO: Still need to get these to work properly
from typing import *

class FedorafigExc(Exception):
  def __init__(self, msg: str, *args: str,
    exc: Optional[BaseException] = None) -> None:
      self.msg: str = msg
      self.args: Tuple[str, ...] = args
      self.exc: Optional[BaseException] = exc

  def __str__(self) -> str:
    if self.exc is not None: return ' '.join((
      "Accompanying error:", str(self.exc)))
    return ' '.join(('fedorafig:', f'{self.msg}:', *self.args))


class LogExc(Exception):
  def __init__(self, exc: BaseException) -> None:
    import logging; from cmn import LOG_FILE
    logging.basicConfig(
      filename=LOG_FILE,
      level=logging.ERROR,
      format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.error(str(exc), exc_info=exc)
    print("fedorafig:", "Unforeseen error:")
    print(str(exc))
