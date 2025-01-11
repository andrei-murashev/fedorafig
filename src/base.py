from os import path; from typing import *
import cmn, err

def write_pkg_list(fh) -> None:
  from subprocess import PIPE
  out = cmn.shell('dnf list installed', stdout=PIPE)
  out = cmn.shell('awk {print\\ $1}', input=out.stdout, stdout=PIPE)
  cmn.shell('tail -n +2', input=out.stdout, stdout=fh)


def create(base_name: str) -> None:
  cmn.shell('mkdir -p', cmn.BASES_PATH)
  base_path: str = path.join(cmn.BASES_PATH, base_name)

  if not path.exists(base_path):
    with open(base_path, 'w') as fh: write_pkg_list(fh); return

  print("Path already exists")
  ans: str = input("Overwrite path? [y/N]: ")
  if ans == 'y' or ans == 'Y':
    with open(base_path, 'w') as fh: write_pkg_list(fh)


def new_diff(new_base_path: str, cur_base_path: str) -> None:
  with open(new_base_path, 'w') as fh: write_pkg_list(fh)
  with open(cur_base_path, 'r') as cur_fh, open(new_base_path, 'r') as new_fh:
    cur_base_lines = cur_fh.readlines()
    new_base_lines = new_fh.readlines()
  from difflib import unified_diff
  diff = unified_diff(
    cur_base_lines,
    new_base_lines,
    fromfile=new_base_path,
    tofile=cur_base_path,
    lineterm=''
  )


def restore(base_name: str) -> None:
  cur_base_path: str = '/tmp/fedorafig_tmp_base'
  old_base_path: str = path.join(cmn.BASES_PATH, base_name)
  if path.exists(cur_base_path): cmn.shell('rm -rf', cur_base_path)
  with open(cur_base_path, 'w') as fh: write_pkg_list(fh)
  if not path.exists(old_base_path): raise err.FedorafigExc(
    "File does not exist", old_base_path)

  with open(cur_base_path, 'r') as cur_fh, open(old_base_path, 'r') as old_fh:
    cur_base_lines: List[str] = cur_fh.readlines()
    old_base_lines: List[str] = old_fh.readlines()

  new_base_path: str = '/tmp/fedorafig_tmp_base_new'; new_base_lines: List[str]
  from difflib import unified_diff
  diff: Iterator[str] = unified_diff(
    old_base_lines,
    cur_base_lines,
    fromfile=old_base_path,
    tofile=cur_base_path,
    lineterm=''
  )
  
  for line in list(diff)[2:]:
    pkg: str = line[1:line.rfind('.')]

    from subprocess import CompletedProcess; out: CompletedProcess
    if line.startswith('+'):
      out = cmn.shell('dnf remove --assumeno', pkg, check=False)
      if out.returncode == 1:
        cmn.shell('dnf remove -y', pkg)
        new_diff(new_base_path, cur_base_path)
      elif out.returncode == 0: pass
      else: raise err.FedorafigExc("Unexpected `dnf` exit code",
        str(out.returncode))

    if line.startswith('-'):
      out = cmn.shell('dnf install --assumeno', pkg, check=False)
      if out.returncode == 1:
        cmn.shell('dnf install -y', pkg)
        new_diff(new_base_path, cur_base_path)
      elif out.returncode == 0: pass
      else: raise err.FedorafigExc("Unexpected `dnf` exit code",
        str(out.returncode))
