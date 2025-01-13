# IMPORTS ======================================================================
# DEPENDENCY: dnf-plugins-core
from os import path; from typing import *
import cmn, err
REPOS_DONE = False

# MAIN CONFIGURATION APPLICATION FUNCTION ======================================
def run(args: cmn.ArgsDict) -> None:
  from check import calc_checksum, extract_entries
  fpath: str = path.join(cmn.CFG.path, str(args['CFG_FILE']))

  checksum_old: str
  checksum_cur: str = calc_checksum(fpath, cmn.COPIES_PATH,
    cmn.REPOS_PATH, cmn.SCRIPTS_PATH, cmn.COMMON_PATH)
  checksum_path: str = path.join(
    cmn.STATE_DIR, f'{path.basename(fpath)}.sha256')
  if path.isfile(checksum_path):
    with open(checksum_path, 'r') as fh: checksum_old = fh.readline().strip()
  if not (path.isfile(checksum_path) and checksum_cur == checksum_old) and \
    not args['no_check']:
      cmd: str = 'fedorafig'
      if bool(args['verbose']): cmd += ' -v'
      elif bool(args['quiet']): cmd += ' -q'
      cmd += ' check'
      if bool(args['interactive']): cmd += ' -i'
      cmn.shell(cmd, fpath, no_sudo=True)

  with open(fpath, 'r') as fh: from json5 import load; data = load(fh)

  entries = extract_entries(data)
  cmn.collect_entries(entries)

  flags = [args['repos_include'], args['pkgs_include'], args['copies_include'], 
    args['prerun_scripts_include'], args['postrun_scripts_include']]

  if True not in flags:
    prerun_scripts_do(); repos_do(); pkgs_do()
    copies_do(); postrun_scripts_do()
  if args['prerun_scripts_include']: prerun_scripts_do()
  if args['repos_include']: repos_do()
  if args['pkgs_include']: pkgs_do()
  if args['copies_include']: copies_do()
  if args['postrun_scripts_include']: postrun_scripts_do()

def repos_do() -> None:
  cmn.shell('cp -rf /etc/yum.repos.d/ /etc/yum.repos.d.bak || True')
  cmn.shell('rm -rf /etc/yum.repos.d/ || True')
  cmn.shell('mkdir -p /etc/yum.repos.d/')
  cmn.shell('cp -rf', cmn.REPOS_PATH, '/etc/yum.repos.d/')
  
  all_repos_enable: bool = False
  repos_enable: List[str] = ['--set-enabled']
  for entry in cmn.ENTRIES:
    if '*' in entry.repos and not entry.pkgs: all_repos_enable = True; break
    elif not entry.pkgs: repos_enable += entry.repos
  cmn.shell('dnf config-manager', *repos_enable)
  if all_repos_enable:
    cmn.shell('dnf config-manager --set-enabled', *cmn.REPOLIST)

  REPOS_DONE = True


def pkgs_do() -> None:
  cmn.shell('dnf clean all')
  if not REPOS_DONE: repos_do()
  for entry in cmn.ENTRIES:
    if entry.repos and '*' in entry.pkgs:
      cmn.shell('dnf install -y --enablerepo=*', *entry.pkgs)
    elif entry.repos and entry.pkgs:
      cmn.shell(f'dnf install -y', *[f'--repo={repo}'
        for repo in entry.repos], *entry.pkgs)
    elif not entry.repos and entry.pkgs:
      cmn.shell('dnf install -y', *entry.pkgs)


def copies_do() -> None:
  for entry in cmn.ENTRIES:
    for copy_paths in entry.copies:
      cmn.shell('mkdir -p', *copy_paths[1:])
      cmn.shell('cp -rf', *copy_paths)

def prerun_scripts_do() -> None:
  for entry in cmn.ENTRIES:
    for script in entry.prerun_scripts:
      cmn.shell('chmod u+x', script); cmn.shell(script)

def postrun_scripts_do() -> None:
  for entry in cmn.ENTRIES:
    for script in entry.postrun_scripts:
      cmn.shell('chmod u+x', script); cmn.shell(script)
