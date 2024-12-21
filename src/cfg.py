# System imports
import os
import sys
import time
import subprocess

# Local imports
import errors


def resolve_path(path):
  try: path = os.path.realpath(os.path.abspath(os.path.expanduser(path)))
  except Exception as e: raise errors.FedorafigException(
    "Unable to resolve path", path, exc=e)
  return path

# Path constants
CFG_DIR = resolve_path('~/.config/fedorafig')
PROG_DIR = resolve_path('~/.local/lib/fedorafig')
EXEC_DIR = resolve_path('~/.local/bin/')
STATE_DIR = resolve_path('~/.local/state/fedorafig')

if sys.argv[0] == 'src/cfg.py':
  os.environ['CFG_DIR'] = CFG_DIR
  os.environ['PROG_DIR'] = PROG_DIR
  os.environ['EXEC_DIR'] = EXEC_DIR
  os.environ['STATE_DIR'] = STATE_DIR
  for key, val in os.environ.items():
    print(f"export {key}={val}")

CFGS_DIR = os.path.join(CFG_DIR, 'configs')
REPOS_DIR = os.path.join(CFG_DIR, 'repos')
SCRIPTS_DIR = os.path.join(CFG_DIR, 'scripts')
COMMON_DIR = os.path.join(CFG_DIR, 'common')
STATE_FILE = os.path.join(STATE_DIR, 'config.txt')


def sudo_refresh():
  while True:
    try: subprocess.run(['sudo', '-v'], check=True)
    except subprocess.CalledSubprocessError as e:
      raise errors.FedorafigException('', exc=e) # TODO
    time.sleep(60)


def makedirs_if_need(dpath):
  try: os.makedirs(dpath, exist_ok=True)
  except Exception as e: raise errors.FedorafigException(
    "Unable to make directory and its parents", dpath, exc=e)


def set_cfg_dir(dpath):
  if not os.path.isdir(resolve_path(dpath)):
    raise errors.FedorafigException("Directory not found", dpath)

  with open(STATE_FILE, 'w') as fh: fh.write(dpath)

  import inspect
  frame = inspect.currentframe().f_back
  caller_file = frame.f_code.co_filename
  if os.path.basename(caller_file) == 'argparse.py': return dpath


def get_cfg_dir(dpath):
  if not os.path.isfile(STATE_FILE): return

  global CFG_DIR
  with open(STATE_FILE, 'r') as fh: CFG_DIR = fh.readline().strip()


# Constants for later use
get_cfg_dir(CFG_DIR)
REPOS_N_PKGS = []
SYS_N_CFG_DIRS = []
SCRIPT_FILES = []
