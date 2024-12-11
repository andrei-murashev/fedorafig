def exit1(msg):
  print(msg)
  exit(1)


"""Exceptions that are used to let `argparse` know that it should exit with an 
error, instead of `python3`, and traceback will be shown."""

class CheckException(Exception):
  """Used for when checking the configuration directory and file syntax."""
  pass

class RunException(Exception):
  """Used for when applying the configuration."""
  pass
