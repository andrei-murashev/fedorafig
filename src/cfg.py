import os

def getpath(path):
  return os.path.realpath(os.path.abspath(os.path.expanduser(path)))


CFG_DIR_REL = f'/home/{os.environ.get('USER')}/.config/fedorafig'
CFG_DIR = getpath(CFG_DIR_REL)
