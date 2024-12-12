import os
import time
import subprocess

def getpath(path):
  return os.path.realpath(os.path.abspath(os.path.expanduser(path)))

def sudo_refresh():
  try:
    while True:
      subprocess.run(['sudo', '-v'], check=True)
      time.sleep(60)
  except Exception:
    raise Exception("Could not validate sudo password")
    # TODO: raise this exception to argparse.

CFG_DIR_REL = f'/home/{os.environ.get('USER')}/.config/fedorafig'
CFG_DIR = getpath(CFG_DIR_REL)
