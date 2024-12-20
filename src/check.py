# System imports
import os
import sys
import json
import glob
import hashlib
import subprocess

# Local packages
import cfg
import errors

# NOTE:
# I have decided that the `repo` entry must be the actual name of the repos-
# itroy, not the name of the repo files. The repos that will be initially
# enabled will be ones specified in `repos`. It is the user's responsibility
# to understand their `.repo` files.


class Check():
  def __init__(self, args):
    self.args = args
    self.checksum = None
    self.file = args['CFG_FILE']

    fpath = os.path.join(cfg.CFG_DIR, self.file)
    if not os.path.isfile(fpath): raise errors.FedorafigException(
      "File not found", fpath)
    with open(os.path.join(cfg.CFG_DIR, self.file)) as fh:
      self.data = json.load(fh)

    # if you are performing `run` without checking, you just need to
    # collect all the values
    if sys.argv[1] == 'run': self.__check_syntax(collect_only=True); return

    # Check that there are no contradicting options
    checksum_yes \
      = {key: args[key] for key in ['only_checksum', 'show_checksum']}
    checksum_no \
      = {key: args[key] for key in ['no_checksum']}

    tmp_args \
      = [key for key, val in (checksum_yes | checksum_no).items() if val]
    dict_disj = lambda bool_dict: True in bool_dict.values()

    if dict_disj(checksum_yes) and dict_disj(checksum_no):
      tmp_args = [f'--{arg.replace('_', '-')}' for arg in tmp_args]
      raise errors.FedorafigException("Conflicting options", *tmp_args)

    # Run the actual checking
    if not args['keep_checksums']: self.__delete_checksums()
    if not args['only_checksum']: self.__check_syntax()
    if not args['no_checksum']:
      self.checksum = self.calc_checksum(self.file)
      self.__save_checksum()
    if args['show_checksum']:
      print(f"{self.file} checksum: {self.checksum}")


  def __delete_checksums(self):
    matches = glob.glob(os.path.join(cfg.STATE_DIR, '*.sha256'))

    for match in matches:
      try: os.remove(match)
      except Exception as e: raise errors.FedorafigException(
        "Unable to remove checksum file", match, exc=e)


  def __check_syntax(self, collect_only=False):
    # Collecting items for checking
    for key, entry in self.data.items():
      if key == '_COMMENT': continue

      if not isinstance(entry, dict): raise errors.FedorafigException(
        "Entry is not a JSON object", entry)

      cfgpath, syspath, pkg, repo, script = None, None, None, None, None

      for subkey, subentry in entry.items():
        if subkey == '_COMMENT': continue
        
        elif subkey == 'syspath':
          syspath = cfg.resolve_path(subentry)

        elif subkey == 'cfgpath':
          cfgpath = os.path.join(cfg.CFGS_DIR, subentry)

        elif subkey == 'repo':
          repo = subentry

        elif subkey == 'pkg':
          pkg = subentry

        elif subkey == 'script':
          script = os.path.join(cfg.SCRIPTS_DIR, subentry)

        else: raise errors.FedorafigException("Invalid key found", subkey)

      if repo or pkg: cfg.REPOS_N_PKGS.append((repo, pkg))
      if syspath or cfgpath: cfg.SYS_N_CFG_DIRS.append((syspath, cfgpath))
      if script: cfg.SCRIPT_FILES.append(script)
    
    # Checking existence of paths
    if collect_only: return

    for syspath, cfgpath in cfg.SYS_N_CFG_DIRS:
      if not os.path.isdir(cfgpath):
        raise errors.FedorafigException("cfgpath not found", syspath)

      if not os.path.isdir(syspath):
        try: os.makedirs(syspath, exist_ok=True)
        except Exception as e: raise errors.FedorafigException(
          "Unable to find directory or make it and its parents",
          syspath, exc=e)

      if not (bool(syspath) == bool(cfgpath)): raise errors.FedorafigException(
        "syspath and cfgpath were not found together", syspath, cfgpath)

    for script in cfg.SCRIPT_FILES:
      if not os.path.isfile(script): raise errors.FedorafigException(
        "script not found", script)

    # Checking existence of repos and packages
    cmd = ['dnf', f'--setopt=reposdir={cfg.REPOS_DIR}', 'repolist', 'all']
    try: out = subprocess.run(cmd, text=True, check=True,
      stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e: raise errors.FedorafigException(
      ".repo file incorrectly formatted", exc=e)

    cmd = ['awk', '{print $1}']
    out = subprocess.run(cmd, text=True, input=out.stdout, check=True, 
      stdout=subprocess.PIPE)
    cmd = ['tail', '-n', '+2']
    out = subprocess.run(cmd, text=True, input=out.stdout, check=True, 
      stdout=subprocess.PIPE)

    if not (repos := out.stdout.splitlines()): raise errors.FedorafigException(
      "No repos found")

    for repo, pkg in cfg.REPOS_N_PKGS:
      if repo == 'all': continue

      elif repo and repo not in repos: raise errors.FedorafigException(
        "repo does not exist", repo)

      elif pkg and not repo:
        try: subprocess.run(['dnf', f'--setopt=reposdir={cfg.REPOS_DIR}',
          'repoquery', pkg], check=True, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError: raise errors.FedorafigException(
          "Unable to find package", pkg)

      elif pkg and repo:
        try: subprocess.run([
          'dnf', f'--setopt=reposdir={cfg.REPOS_DIR}',
          'repoquery', f'--repo={repo}', pkg],
          check=True, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
          raise errors.FedorafigException(
            "Unable to find package from repo", pkg, repo)


  @staticmethod
  def calc_checksum(cfg_file):
    hasher = hashlib.sha256()
    dpaths = [cfg.CFGS_DIR, cfg.REPOS_DIR, cfg.SCRIPTS_DIR]

    for dpath in dpaths:
      for root, _, files in os.walk(dpath):
        for file in sorted(files):
          path = os.path.join(root, file)
          with open(path, 'rb') as fh:
            while chunk := fh.read(8192): hasher.update(chunk)
    
    fpath = os.path.join(cfg.CFG_DIR, cfg_file)
    with open(fpath, 'rb') as fh:
      while chunk := fh.read(8192): hasher.update(chunk)

    return hasher.hexdigest()


  def __save_checksum(self):
    fname = f'{self.file}.sha256'
    hash_fpath = os.path.join(cfg.STATE_DIR, fname)
    with open(hash_fpath, 'w') as fh: fh.write(self.checksum)
