# System imports
from os import path, environ
from typing import Optional, List, Dict
import subprocess as sp
import time

# Local imports
import err

# COMMON FUNCTIONS =============================================================
def resolve_path(apath: str) -> str:
  try: apath = path.abspath(path.expanduser(apath))
  except Exception as e: raise err.FedorafigExc(
    "Unable to resolve path", apath, exc=e)
  return apath


def resolve_syml(apath: str) -> str:
  try: apath = path.realpath(path.abspath(path.expanduser(apath)))
  except Exception as e: raise err.FedorafigExc(
    "Unable to resolve potential symbolic link", apath, exc=e)
  return apath


def sudo_refresh() -> None:
  while True:
    try: sp.run(['sudo', '-v'], check=True, stderr=sp.PIPE)
    except sp.CalledProcessError as e: raise err.FedorafigExc(
      e.stderr)


# HARDCODED CONSTANTS ==========================================================
PROG_DIR: str     = resolve_path('~/.local/lib/fedorafig/')
EXEC_DIR: str     = resolve_path('~/.local/bin/')
STATE_DIR: str    = resolve_path('~/.local/state/fedorafig/')
LOG_FILE: str     = path.join(STATE_DIR, 'log.txt')
CFG_PTR_FILE: str = path.join(STATE_DIR, 'cfg_ptr.txt')

# CHANGING THE CONFIGURATION DIRECTORY =========================================
CFGS_PATH: str; REPOS_PATH: str; SCRIPTS_PATH: str; COMMON_PATH: str

class CfgDir():
  def __init__(self) -> None:
    self._path = resolve_path('~/.config/fedorafig/')

  @property
  def path(self) -> str:
    if path.isfile(CFG_PTR_FILE):
      with open(CFG_PTR_FILE, 'r') as fh: self._path = fh.readline().strip()
    global CFGS_PATH, REPOS_PATH, SCRIPTS_PATH, COMMON_PATH
    CFGS_PATH    = path.join(self._path, 'configs', '.')
    REPOS_PATH   = path.join(self._path, 'repos', '.')
    SCRIPTS_PATH = path.join(self._path, 'scripts', '.')
    COMMON_PATH  = path.join(self._path, 'common', '.')
    print(CFGS_PATH, REPOS_PATH, SCRIPTS_PATH, COMMON_PATH)
    return self._path


  @path.setter
  def path(self, dpath: str) -> None:
    if not path.isdir(resolve_path(dpath)): raise err.FedorafigExc(
      "Directory not found", dpath)
    with open(CFG_PTR_FILE, 'w') as fh: fh.write(dpath)
    self._path = dpath

# COMMON CONSTANTS =============================================================
from typing import Callable, Any
type ArgsDict = dict[str, str | bool | Callable[..., Any]]
CFG = CfgDir(); print(CFG.path)
def set_cfg_dir(dir: str) -> str: CFG.path = dir; return dir

if __name__ == '__main__':
  print(f'export CFG_DIR="{CFG.path}"')
  print(f'export PROG_DIR="{PROG_DIR}"')
  print(f'export EXEC_DIR="{EXEC_DIR}"')
  print(f'export STATE_DIR="{STATE_DIR}"')
  raise SystemExit


# MANAGING ENTRIES =============================================================
cmd: List[str]; out: sp.CompletedProcess

cmd = ['dnf', f'--setopt=reposdir={REPOS_PATH}', 'makecache']
try: sp.run(cmd, check=True)
except sp.CalledProcessError as e: raise err.FedorafigExc(e.stderr)

cmd = ['dnf', f'--setopt=reposdir={REPOS_PATH}', 'repolist', 'all']
try: out = sp.run(cmd, text=True, check=True, stdout=sp.PIPE)
except sp.CalledProcessError as e: raise err.FedorafigExc(e.stderr)

cmd = ['awk', '{print $1}']
out = sp.run(cmd, text=True, input=out.stdout, check=True, stdout=sp.PIPE)
cmd = ['tail', '-n', '+2']
out = sp.run(cmd, text=True, input=out.stdout, check=True, stdout=sp.PIPE)
if not (REPOLIST := out.stdout.splitlines()): raise err.FedorafigExc(
  "No repos found")


class Entry():
  type SelfType = Dict[str, List[str | List[str]]]
  def __init__(self, entry: SelfType):
    for key, val in entry.items(): setattr(self, key, val)
    print(REPOLIST)


ENTRIES: List[Entry] = []
def collect_entries(entries: List[Entry.SelfType]) -> None:
  for entry in entries: ent: Entry = Entry(entry); ENTRIES.append(ent)
