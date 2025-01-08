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
  if path.exists(base_path): raise err.FedorafigExc(
    "Path already exists", base_path)
  with open(base_path, 'w') as fh: write_pkg_list(fh)


def restore(base_name: str) -> None:
  cur_base_path: str = '/tmp/fedorafig_tmp_base'
  old_base_path: str = path.join(cmn.BASES_PATH, base_name)
  if path.exists(cur_base_path): cmn.shell('rm -rf', cur_base_path)
  with open(cur_base_path, 'w') as fh: write_pkg_list(fh)
  if not path.exists(old_base_path): raise err.FedorafigExc(
    "File does not exist", old_base_path)
  # TODO: Ask if user wants to overwrite path
  with open(cur_base_path, 'r') as cur_fh, open(old_base_path, 'r') as old_fh:
    cur_base_lines: List[str] = cur_fh.readlines()
    old_base_lines: List[str] = old_fh.readlines()

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
    if line.startswith('+'): cmn.shell('dnf remove -y', pkg)
    if line.startswith('-'): cmn.shell('dnf install -y', pkg)
    # TODO: speed up by recreateing base files because multiple packages are likely to disappear
