# IMPORTS ======================================================================
from os import path, environ; from typing import *
import subprocess as sp; import err

# COMMON FUNCTIONS =============================================================
def shell(*cmds: str, no_sudo: bool = False, split_str: str = ' ',
  **kwargs: Any) -> sp.CompletedProcess:
    from os import environ
    subcmds: List[str] = [subcmd.replace('__SPACE__', ' ') for cmd in cmds
      for subcmd in cmd.replace('\\ ', '__SPACE__').split(' ')]
    try: subcmds.insert(0, 'sudo') if environ['SUDO_USER'] \
      and not no_sudo else None
    except: print('USER IS NOT ROOOOOT!!!')
    try: out: sp.CompletedProcess = sp.run(subcmds, text=True, check=True,
      stderr=sp.PIPE, **kwargs)
    except sp.CalledProcessError as e: raise err.LogExc(e.stderr)
    print(subcmds); return out

def resolve_path(apath_og: str) -> str:
  from os import environ
  try: apath: str = apath_og.replace('~',
    path.join('/home', environ['SUDO_USER']))
  except: apath = path.expanduser(apath_og)

  try:
    apath = path.abspath(apath)
    if apath_og.endswith('/.'): apath += '/.'
  except Exception as e: raise err.FedorafigExc(
    "Unable to resolve path", apath, exc=e)
  return apath

# HARDCODED CONSTANTS ==========================================================
PROG_DIR: str     = resolve_path('~/.local/lib/fedorafig/')
EXEC_DIR: str     = resolve_path('/usr/local/bin/')
STATE_DIR: str    = resolve_path('~/.local/state/fedorafig/')
LOG_FILE: str     = path.join(STATE_DIR, 'log.txt')
CFG_PTR_FILE: str = path.join(STATE_DIR, 'cfg_ptr.txt')

# CHANGING THE CONFIGURATION DIRECTORY =========================================
COPIES_PATH: str; REPOS_PATH: str; SCRIPTS_PATH: str; COMMON_PATH: str

class CfgDir():
  def __init__(self) -> None:
    self._path = resolve_path('~/.config/fedorafig/')

  @property
  def path(self) -> str:
    if path.isfile(CFG_PTR_FILE):
      with open(CFG_PTR_FILE, 'r') as fh: self._path = fh.readline().strip()
    global COPIES_PATH, REPOS_PATH, SCRIPTS_PATH, COMMON_PATH
    COPIES_PATH  = path.join(self._path, 'copies')
    REPOS_PATH   = path.join(self._path, 'repos', '.')
    SCRIPTS_PATH = path.join(self._path, 'scripts')
    COMMON_PATH  = path.join(self._path, 'common')
    return self._path

  @path.setter
  def path(self, dpath: str) -> None:
    if not path.isdir(resolve_path(dpath)): raise err.FedorafigExc(
      "Directory not found", dpath)
    with open(CFG_PTR_FILE, 'w') as fh: fh.write(dpath)
    self._path = dpath

# COMMON CONSTANTS =============================================================
from typing import Callable, Any
type ArgsDict = Dict[str, str | bool | Callable[..., Any]];
CFG = CfgDir(); CFG.path
def set_cfg_dir(dir: str) -> str: CFG.path = dir; return dir

if __name__ == '__main__':
  print(f'export CFG_DIR="{CFG.path}"')
  print(f'export PROG_DIR="{PROG_DIR}"')
  print(f'export EXEC_DIR="{EXEC_DIR}"')
  print(f'export STATE_DIR="{STATE_DIR}"')
  exit(0)

out: sp.CompletedProcess; print(REPOS_PATH)
out = shell(f'dnf --setopt=reposdir={REPOS_PATH} repolist all', stdout=sp.PIPE)
out = shell('awk {print\\ $1}', input=out.stdout, stdout=sp.PIPE)
out = shell('tail -n +2', input=out.stdout, stdout=sp.PIPE)
if not (REPOLIST := out.stdout.splitlines()): raise err.FedorafigExc(
  "No repos found")
print(REPOLIST)

# MANAGING ENTRIES =============================================================
class Entry():
  type SelfType = Dict[str, List[str | List[str]]]
  def __init__(self, entry: SelfType):
    self.repos: List[str] = []
    self.pkgs: List[str] = []
    self.prerun_scripts: List[str] = []
    self.postrun_scripts: List[str] = []
    self.copies: List[List[str]] = []

    pkeys = ['repos', 'pkgs', 'copies', 'prerun_scripts', 'postrun_scripts']
    for key, val in entry.items():
      if key in pkeys: setattr(self, key, val)
      else: raise err.FedorafigExc("Invalid key", key)
    
    self.copies = [[path.join(COPIES_PATH, paths[0]),
      *[resolve_path(apath) for apath in paths[1:]]]
      for paths in self.copies if self.copies]
    self.prerun_scripts = [path.join(SCRIPTS_PATH, name) \
      for name in self.prerun_scripts if self.prerun_scripts]
    self.postrun_scripts = [path.join(SCRIPTS_PATH, name) \
      for name in self.postrun_scripts if self.postrun_scripts]
    print(self.__dict__, end='\n\n')

ENTRIES: List[Entry] = []
def collect_entries(entries: List[Entry.SelfType]) -> None:
  for entry in entries: ent: Entry = Entry(entry); ENTRIES.append(ent)
