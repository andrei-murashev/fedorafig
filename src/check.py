# TODO: See where I can leave out `text=True` in `sp`

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
    self.fname: str = args['CFG_FILE']
    self.checksum: str

    fpath = path.join(cmn.CFG.path, self.fname)
    if not path.isfile(fpath): raise err.FedorafigExc(
      "File not found", fpath)
    with open(path.join(cmn.CFG.path, self.fname), 'r') as fh:
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
      self.check_syntax(cmn.ENTRIES, interactive=bool(self.args['interactive']))
    if not args['no_checksum']:
      self.checksum = self.calc_checksum(path.join(cmn.CFG.path, self.fname),
        cmn.COPIES_PATH, cmn.REPOS_PATH, cmn.SCRIPTS_PATH, cmn.COMMON_PATH)
      self.__save_checksum()
    if args['show_checksum']:
      print(f"{self.fname} checksum: {self.checksum}")

  
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
  def check_syntax(entries: List[cmn.Entry], interactive: bool = True) -> None:
    cmd: List[str]; out: sp.CompletedProcess

    cmd = ['dnf', f'--setopt=reposdir={cmn.REPOS_PATH}',
      '--enablerepo=*', 'makecache']
    try: out = sp.run(cmd, check=True, stderr=sp.PIPE)
    except sp.CalledProcessError as e: raise err.FedorafigExc(e.stderr)

    cmd = ['dnf', f'--setopt=reposdir={cmn.REPOS_PATH}', 'repolist', 'all']
    print(' '.join(cmd))
    try: out = sp.run(cmd, text=True, check=True, stdout=sp.PIPE)
    except sp.CalledProcessError as e: raise err.FedorafigExc(e.stderr)

    cmd = ['awk', '{print $1}']
    out = sp.run(cmd, text=True, input=out.stdout, check=True, stdout=sp.PIPE)
    cmd = ['tail', '-n', '+2']
    out = sp.run(cmd, text=True, input=out.stdout, check=True, stdout=sp.PIPE)
    if not (repolist := out.stdout.splitlines()): raise err.FedorafigExc(
      "No repos found")
    print(repolist)

    repos_n_pkgs_pairs: List[Tuple[List[str], List[str]]] = []
    script_paths: List[str] = []; copy_paths: List[str] = []
    for entry in entries:
      repos_n_pkgs_pairs += [(entry.repos, entry.pkgs)]
      script_paths += entry.prerun_scripts + entry.postrun_scripts
      copy_paths += [dpath for dpaths in entry.copies for dpath in dpaths]

    for repos, pkgs in (pair for pair in repos_n_pkgs_pairs):
      for repo in repos:
        if repo not in repolist and repo != '*': raise err.FedorafigExc(
          "Repo not found", repo)
      if pkgs and not repos:
        cmd = ['dnf', f'--setopt=reposdir={cmn.REPOS_PATH}', 'repoquery', *pkgs]
      if pkgs and repos:
        repo_enables: List[str] = [f'--enablerepo={repo}' for repo in repos]
        print(repo_enables)
        cmd = ['dnf', f'--setopt=reposdir={cmn.REPOS_PATH}', *repo_enables, 
          'repoquery', *pkgs]
      try: sp.run(cmd, text=True, check=True, stderr=sp.PIPE) if cmd else None
      except sp.CalledProcessError as e: raise err.FedorafigExc(e.stderr)

    for script_path in script_paths:
      if not path.isfile(script_path): raise err.FedorafigExc(
        "File not found", script_path)

    if not path.exists(copy_paths[0]): raise err.FedorafigExc(
      "Copy source does not exist", copy_paths[0])
    for copy_path in copy_paths[1:]:
      dir: str = copy_path[:copy_path.rfind('/')]
      cmd = ['mkdir', '-p', dir]
      
      if copy_path.startswith(cmn.CFG.path) and not path.exists(copy_path):
        raise err.FedorafigExc("Path not found", copy_path)

      elif not path.isdir(dir) and interactive:
        ans = input(f"Create directory {dir} [y/N]: ")
        from itertools import product
        opts: List[Tuple[str, str]] = [('y', 'Y'), ('e', 'E'), ('s', 'S')]
        if ans in [''.join(comb) for comb in product(*opts)] + ['y', 'Y']:
          try: sp.run(cmd, check=True, stderr=sp.PIPE)
          except sp.CalledProcessError as e: raise err.FedorafigExc(e.stderr)
        else: continue
      elif not(path.isdir(dir) or interactive):
        try: sp.run(cmd, check=True, stderr=sp.PIPE)
        except sp.CalledProcessError as e: raise err.FedorafigExc(e.stderr)


  def __delete_checksums(self) -> None:
    matches = glob.glob(path.join(cmn.STATE_DIR, '*.sha256'))
    for match in matches:
      from os import remove
      try: remove(match)
      except Exception as e: raise err.FedorafigExc(
        "Unable to remove checksum file", match, exc=e)


  def __save_checksum(self) -> None:
    fname = f'{self.fname}.sha256'
    fpath = path.join(cmn.STATE_DIR, fname)
    with open(fpath, 'w') as fh: fh.write(self.checksum)


  @staticmethod
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
