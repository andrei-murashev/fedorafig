# System imports
from os import path
from typing import *
import subprocess as sp
import sys, glob

# Package imports
import json5

# Local imports
import cmn, err

class Check():
  def __init__(self, args) -> None:
    self.args: Dict[str, cmn.ArgsDict] = args
    self.file: str = args['CFG_FILE']
    self.checksum: str

    fpath = path.join(cmn.CFG.path, self.file)
    if not path.isfile(fpath): raise err.FedorafigExc(
      "File not found", fpath)
    with open(path.join(cmn.CFG.path, self.file), 'r') as fh:
      try: self.data: dict[str, Any] = json5.load(fh)
      except Exception as e: raise err.FedorafigExc(
        "JSON5 parsing error", exc=e)

    # if sys.argv[1] == 'run': self.__check_syntax(collect_only=True); return

    checksum_yes: Dict[str, bool] \
      = {key: args[key] for key in ['only_checksum', 'show_checksum']}
    checksum_no: Dict[str, bool]  \
      = {key: args[key] for key in ['no_checksum']}
    tmp_args: List[str] \
      = [key for key, val in (checksum_yes | checksum_no).items() if val]

    dict_disj: Callable[[Dict[str, bool]], bool] \
      = lambda bool_dict: True in bool_dict.values()
    if dict_disj(checksum_yes) and dict_disj(checksum_no):
      tmp_args = [f'--{arg.replace('_', '-')}' for arg in tmp_args]
      raise err.FedorafigExc("Confliction options", *tmp_args)

    if not args['keep_checksums']:
      self.__delete_checksums()

    if not args['only_checksum']:
      entries: List[cmn.Entry.SelfType] = self.__check_types()
      cmn.collect_entries(entries)
      self.check_syntax(cmn.ENTRIES)

    if not args['no_checksum']:
      self.checksum = self.calc_checksum(self.file)
      self.__save_checksum()

    if args['show_checksum']:
      print(f"{self.file} checksum: {self.checksum}")

  
  def __check_types(self) -> List[cmn.Entry.SelfType]:
    entries: List[cmn.Entry.SelfType] = []
    for entry in self.data.values():
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


  @staticmethod
  def check_syntax(entries: List[cmn.Entry]) -> None: pass
    # Check if repos exist if they are specified.
    cmd: List[str]; out: sp.CompletedProcess

    cmd = ['dnf', f'--setopt=reposdir={cmn.REPOS_PATH}', 'repolist', 'all']
    try: out = sp.run(cmd, text=True, check=True, stdout=sp.PIPE)
    except sp.CalledProcessError as e: raise err.FedorafigExc(e.stderr)

    cmd = ['awk', '{print $1}']
    out = sp.run(cmd, text=True, input=out.stdout, check=True, stdout=sp.PIPE)
    cmd = ['tail', '-n', '+2']
    out = sp.run(cmd, text=True, input=out.stdout, check=True, stdout=sp.PIPE)
    if not (repolist := out.stdout.splitlines()): raise err.FedorafigExc(
      "No repos found")

    for entry in entry:
      repos_n_pkgs: Tuple[List[str], List[str]] = (entry.repos, entry.pkgs)
      script_paths: List[str] = entry.prerun_scripts + entry.postrun_scripts
      copy_paths: List[str] = \
        [dpath for dpaths in entry.copies for dpath in dpaths]
      print(repos_n_pkgs, script_paths, copy_paths)

    # Check if pkgs exist, and if they are in the specified repos.
    # Check all scripts exists and they are executable.
    # Check if files to be copied exist and if the directories to be copied
    # exist or can be created without elevating permissions.

  def __delete_checksums(self) -> None:
    matches = glob.glob(path.join(cmn.STATE_DIR, '*.sha256'))
    for match in matches:
      from os import remove
      try: remove(match)
      except Exception as e: raise err.FedorafigExc(
        "Unable to remove checksum file", match, exc=e)


  def __save_checksum(self) -> None:
    fname = f'{self.file}.sha256'
    fpath = path.join(cmn.STATE_DIR, fname)
    with open(fpath, 'w') as fh: fh.write(self.checksum)


  @staticmethod
  def calc_checksum(fpath: str) -> str:
    import hashlib
    hasher: hashlib._Hash = hashlib.sha256()
    dpaths: List[str] \
      = [cmn.CFGS_PATH, cmn.REPOS_PATH, cmn.SCRIPTS_PATH, cmn.COMMON_PATH]
    dpaths = [dpath for dpath in dpaths if path.isdir(dpath)]
    
    for dpath in dpaths:
      from os import walk
      for root, _, files in walk(dpath):
        for file in sorted(files):
          ffpath: str = path.join(root, file)
          with open(ffpath, 'rb') as fh:
            chunk: bytes = fh.read(8192)
            while chunk: hasher.update(chunk)

    return hasher.hexdigest()
