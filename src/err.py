# TODO: Figure out why I'm still getting huge error messages
# TODO: Still need to get these to work properly

class FedorafigExc(Exception):
  def __init__(self, msg: str, *args, exc: BaseException | None = None) -> None:
    print("fedorafig:", f"{msg}:", *args)
    if exc is not None: print("Accompanying error:", str(exc))


class LogExc(Exception):
  def __init__(self, exc: BaseException) -> None:
    import logging; from cmn import LOG_FILE
    logging.basicConfig(
      filename=LOG_FILE,
      level=logging.ERROR,
      format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.error(str(exc), exc_info=exc)
    print("fedorafig:", "Unforeseen error:", str(exc))
