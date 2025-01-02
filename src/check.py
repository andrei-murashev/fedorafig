# IMPORTS ======================================================================
from os import path; from typing import *
from subprocess import PIPE; import cmn, err

# CONFIGURATION CHECK ==========================================================
def check(args: cmn.ArgsDict) -> None:
  fpath: str = path.join(cmn.CFG.path, str(args['CFG_FILE']))
  if not path.isfile(fpath): raise err.FedorafigExc("File not found", fpath)
  with open(fpath, 'r') as fh:
    from json5 import load
    try: data: Dict[str, Any] = load(fh)
    except Exception as e: raise err.FedorafigExc(
      "JSON5 parsing error", exc=e)

  checksum_yes: Dict[str, bool] \
    = {key: bool(args[key]) for key in ['only_checksum', 'show_checksum']}
  checksum_no: Dict[str, bool]  \
    = {key: bool(args[key]) for key in ['no_checksum']}
  tmp_args: List[str] \
    = [key for key, val in (checksum_yes | checksum_no).items() if val]

  dict_disj: Callable[[Dict[str, bool]], bool] \
    = lambda bool_dict: True in bool_dict.values()
  if dict_disj(checksum_yes) and dict_disj(checksum_no):
    tmp_args = [f'--{arg.replace('_', '-')}' for arg in tmp_args]
    raise err.FedorafigExc("Confliction options", *tmp_args)

  if not args['keep_checksums']: delete_checksums()
  if not args['only_checksum']:
    entries: List[cmn.Entry.SelfType] = extract_entries(data)
    cmn.collect_entries(entries)
    entries_check(cmn.ENTRIES)
  if not args['no_checksum']:
    checksum = calc_checksum(fpath, cmn.COPIES_PATH,
      cmn.REPOS_PATH, cmn.SCRIPTS_PATH, cmn.COMMON_PATH)
    fpath = path.join(cmn.STATE_DIR, f'{path.basename(fpath)}.sha256')
    with open(fpath, 'w') as fh: fh.write(checksum)
  if args['show_checksum']: print(
    f"{path.basename(fpath)} checksum: {checksum}")

# JSON5 TO ENTRIES LIST ========================================================
def extract_entries(data: Dict[str, Any]) -> List[cmn.Entry.SelfType]:
  entries: List[cmn.Entry.SelfType] = []
  for entry in data.values():
    if not isinstance(entry, Dict): raise err.FedorafigExc(
      "Entry is of an incompatible type", type(entry))
    for key in entry.keys():
      if not isinstance(key, str): raise err.FedorafigExc(
        "Entry key is not a string", "Entry type:", {type(key)})

    for val in entry.values():
      if not isinstance(val, List): raise err.FedorafigExc(
        "Entry value is not a list is not a list", "Value type:", {type(val)})

      for elem in val:
        if isinstance(elem, List):
          elem_list = elem
          if all(isinstance(elem, str) for elem in elem_list): continue
        elif not isinstance(elem, str): raise err.FedorafigExc(
          "Entry value element is not a string", "Value type:", type(val))

    entries.append(entry)
  return entries

# CHECK ENTRY SYNTAX AND PROPERTY EXISTENCE ====================================
def entries_check(entries: List[cmn.Entry]) -> None:
  # NOTE: uncomment later cmn.shell(f'dnf --setopt=reposdir={cmn.REPOS_PATH} --enablerepo=* makecache')

  repos_n_pkgs_pairs: List[Tuple[List[str], List[str]]] = []
  script_paths: List[str] = []; copies: List[List[str]] = []
  for entry in entries:
    repos_n_pkgs_pairs += [(entry.repos, entry.pkgs)]
    script_paths += entry.prerun_scripts + entry.postrun_scripts
    copies += entry.copies

  for repos, pkgs in (pair for pair in repos_n_pkgs_pairs):
    print("REPOS AND PKGS:", repos, pkgs)
    for repo in repos:
      if repo not in cmn.REPOLIST and repo != '*':
        print("matched case 1")
        raise err.FedorafigExc(
        "Repo not found", repo)
    if pkgs and not repos:
      cmn.shell(f'dnf --setopt=reposdir={cmn.REPOS_PATH}',
        'repoquery', ' '.join(pkgs))
      print("matched case 2")
    if pkgs and repos:
      repo_enables: List[str] = [f'--enablerepo={repo}' for repo in repos]
      cmn.shell(f'dnf --setopt=reposdir={cmn.REPOS_PATH}',
        ' '.join(repo_enables), 'repoquery', ' '.join(pkgs))
      print("matched case 3")

  for copy_paths in copies:
    if not path.exists(copy_paths[0]): raise err.FedorafigExc(
      "Path not found", script_paths[0])

# JSON5 TO ENTRIES LIST ========================================================
def delete_checksums() -> None:
  from glob import glob
  matches = glob(path.join(cmn.CFG.path, '*.json5'))
  for match in matches: cmn.shell(f'rm -rf {match}.sha256 || True')

# CALCULATE CHECKSUM FOR DIR OR FILE ===========================================
def calc_checksum(*apaths: str) -> str:
  import hashlib; chunk: bytes
  hasher: hashlib._Hash = hashlib.sha256()
  
  for apath in apaths:
    if path.isfile(apath):
      with open(apath, 'rb') as fh:
        while chunk := fh.read(8192): hasher.update(chunk)

    elif path.isdir(apath):
      from os import walk
      for root, _, files in walk(apath):
        for file in sorted(files):
          fpath: str = path.join(root, file)
          with open(fpath, 'rb') as fh:
            while chunk := fh.read(8192): hasher.update(chunk)
    
    else: raise err.LogExc(Exception("Path not found", apath))

  return hasher.hexdigest()
