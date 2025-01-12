# IMPORTS ======================================================================
from os import path; from typing import *
import cmn, err

# COMMON FUNCTIONS =============================================================
def write_pkg_list(fh) -> None:
  from subprocess import PIPE
  out = cmn.shell('dnf list installed', stdout=PIPE)
  out = cmn.shell('awk {print\\ $1}', input=out.stdout, stdout=PIPE)
  out = cmn.shell('tail -n +2', input=out.stdout, stdout=PIPE)
  out = cmn.shell("cut -f 1 -d .", input=out.stdout, stdout=fh)
  print(out.stdout)

# BASE CREATEION =========================================================
def create(base_name: str) -> None:
  cmn.shell('mkdir -p', cmn.BASES_PATH)
  base_path: str = path.join(cmn.BASES_PATH, base_name)

  if not path.exists(base_path):
    with open(base_path, 'w') as fh: write_pkg_list(fh); return

  print("Path already exists")
  ans: str = input("Overwrite path? [y/N]: ")
  if ans == 'y' or ans == 'Y':
    with open(base_path, 'w') as fh: write_pkg_list(fh)

# BASE RESTORATION =======================================================
def restore(base_name: str) -> None:
  cur_base_path: str = '/tmp/fedorafig_tmp_base'
  old_base_path: str = path.join(cmn.BASES_PATH, base_name)
  if path.exists(cur_base_path): cmn.shell('rm -rf', cur_base_path)
  if not path.exists(old_base_path): err.fedorafig_exc(
    "File does not exist", old_base_path)

  diff = diff_update(old_base_path, cur_base_path); diffs_applied: bool = False
  while not diffs_applied: diff, diffs_applied \
    = diff_apply(diff, old_base_path, cur_base_path)


def diff_apply(diff: Iterator[str], old_base_path: str, cur_base_path: str) \
  -> Tuple[Iterator[str], bool]:
    from subprocess import DEVNULL
    found_diff: bool = False

    for line in list(diff)[2:]:
      pkg = line[1:line.rfind('.')]

      if line.startswith('+'):
        out = cmn.shell('dnf remove --assumeno', pkg,
          check=False, stdout=DEVNULL)
        if out.returncode == 1:
          cmn.shell('dnf remove -y', pkg); found_diff = True; break
        elif out.returncode == 0:
          continue
        else: err.fedorafig_exc(
          "Unexpected `dnf` exit code", str(out.returncode))

      elif line.startswith('-'):
        out = cmn.shell('dnf install --assumeno', pkg,
          check=False, stdout=DEVNULL)
        if out.returncode == 1:
          cmn.shell('dnf install -y', pkg); found_diff = True; break
        elif out.returncode == 0:
          continue
        else: err.fedorafig_exc(
          "Unexpected `dnf` exit code", str(out.returncode))

    if found_diff:
      diff = diff_update(old_base_path, cur_base_path)
      return diff, False
    else: return diff, True


def diff_update(old_base_path: str, cur_base_path: str) -> Iterator[str]:
  with open(cur_base_path, 'w') as fh: write_pkg_list(fh)
  with open(cur_base_path, 'r') as cur_fh, open(old_base_path, 'r') as old_fh:
    cur_base_lines: List[str] = cur_fh.readlines()
    old_base_lines: List[str] = old_fh.readlines()

  from difflib import unified_diff
  diff: Iterator[str] = unified_diff(
    old_base_lines,
    cur_base_lines,
  )

  return diff
