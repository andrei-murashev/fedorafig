# System packages
import os
import json
import glob
import hashlib
import subprocess

# Local packages
import cfg
import errors


class CheckException(Exception):
  """Exception that lets `argparse` know that it should exit with an error,
  instead of `python3`, and no traceback will be shown."""
  pass



class Check():
  def __init__(self, arg_list):
    self.args = vars(arg_list)
    self.checksum = ''

    if not self.args['keep_checksums']: self.__delete_checksums()
    # TODO: Consider whether this option is redundant ^.
    if not self.args['only_checksum']: self.__check_syntax()

    if not self.args['no_checksum']: 
      self.checksum = self.calc_checksum(self.args['CFG_FILE'])
      self.__save_checksum()

    if self.args['show_checksum']:
      print(f"{self.args['CFG_FILE']} checksum: {self.checksum}")


  def __delete_checksums(self):
    state_dir = os.path.expanduser('~/.local/state/fedorafig')

    try:
      os.makedirs(state_dir, exist_ok=True)
    except FileExistsError:
      os.remove(state_dir)
      exit(1)

    pattern = '*.sha256'
    matches = glob.glob(f'{state_dir}/{pattern}')
    
    for match in matches:
      try: os.remove(match)
      except PermissionError:
        errors.exit1(f"No permission to remove file: {match}")
      except IsADirectoryError:
        errors.exit1(f"Cannot remove a directory: {match}")
      except OSError:
        errors.exit1(f"OS error prevents from deletion: {match}")


  def __check_syntax(self):
    fpath = os.path.join(cfg.CFG_DIR, self.args['CFG_FILE'])
    if not (os.path.exists(fpath) and os.path.isfile(fpath)):
      raise CheckException(
        f"Configuration not found: {fpath}")
    
    data = None
    with open(fpath, 'r') as fh:
      data = json.load(fh)

    repos_n_pkgs = []

    for key, entry in data.items():
      if key == '_COMMENT':
        continue

      if not isinstance(entry, dict):
        raise CheckException(f"Value is not an object for key: {key}")
      
      found_syspath = False
      found_cfgpath = False
      pkg = ''
      repo = ''

      for subkey, subentry in entry.items():
        if subkey == 'syspath':
          found_syspath = True
          syspath = cfg.getpath(subentry)
          if not (os.path.exists(syspath) and os.path.isdir(syspath)):
            os.makedirs(syspath)

        elif subkey == 'cfgpath':
          found_cfgpath = True
          cfgpath = cfg.getpath(os.path.join(cfg.CFG_DIR, 'configs', subentry))
          if not os.path.exists(cfgpath):
            raise CheckException(
              f"cfgpath does not exists or is not a file: {cfgpath}")

        elif subkey == 'repo':
          repo = subentry

        elif subkey == 'pkg':
          pkg = subentry

        elif subkey == 'script':
          script_path = cfg.getpath(os.path.join(cfg.CFG_DIR, 'scripts',
            subentry))
          if not (os.path.exists(script_path) and os.path.isfile(script_path)):
            raise CheckException(f"Script not found: {script_path}")

        elif subkey == '_COMMENT':
          pass

        else:
          raise CheckException(f"Subkey not recogised: {subkey}")

      if repo or pkg: repos_n_pkgs.append((repo, pkg))

      if found_syspath != found_cfgpath:
        raise CheckException("syspath and cfgpath do not accompany each other")

    tmp_repos_dir = '/tmp/fedorafig_repos'
    if os.path.exists(tmp_repos_dir):
      subprocess.run(['rm', '-rf', tmp_repos_dir], check=True)
    os.mkdir(tmp_repos_dir)

    for repo, pkg in repos_n_pkgs:
      if repo == 'all':
        repo_paths = os.path.join(cfg.CFG_DIR, 'repos/*')
        for path in glob.glob(repo_paths):
          if os.path.isfile(path):
            subprocess.run(['cp', path, '/tmp/fedorafig_repos'], check=True)
        break

      elif repo and not pkg:
        print("REPO AND NOT PKG:", repo)
        path = os.path.join(cfg.CFG_DIR, 'repos', f'{repo}.repo')
        if not os.path.isfile(path):
          raise CheckException(f"Unable to get to find repo file: {path}")
        subprocess.run(['cp', path, '/tmp/fedorafig_repos'], check=True)

    try:
      subprocess.run(['dnf', '--setopt=reposdir=/tmp/fedorafig_repos', \
        'repolist'], check=True, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
      raise CheckException(e.stderr.strip())

    for repo, pkg in repos_n_pkgs:
      if pkg and not repo:
        try: subprocess.run(['dnf', '--setopt=reposdir=/tmp/fedorafig_repos', \
          'info', pkg], check=True)
        except subprocess.CalledProcessError: raise CheckException(
          f"Unable to find package: {pkg}")

      elif pkg and repo:
        try:
          subprocess.run(['dnf', '--setopt=reposdir=/tmp/fedorafig_repos', \
            f'--enablerepo={repo}', 'info', pkg], check=True)
        except subprocess.CalledProcessError:
          raise CheckException(
            f"Unable to get package from repo: {pkg} from {repo}")


  @staticmethod
  def calc_checksum(cfg_file):
    hasher = hashlib.sha256()

    dpaths = [
      os.path.join(cfg.CFG_DIR, 'repos'),
      os.path.join(cfg.CFG_DIR, 'configs'),
      os.path.join(cfg.CFG_DIR, 'scripts')
    ]

    for dpath in dpaths:
      for root, _, files in os.walk(dpath):
        for file in sorted(files):
          path = os.path.join(root, file)
          with open(path, 'rb') as fh:
            while chunk := fh.read(8192):
              hasher.update(chunk)

    fpath = os.path.join(cfg.CFG_DIR, cfg_file)
    with open(fpath, 'rb') as fh:
      while chunk := fh.read(8192):
        hasher.update(chunk)

    return hasher.hexdigest()


  def __save_checksum(self):
    hash_name = self.args['CFG_FILE']
    hash_name = hash_name[:hash_name.index('.')]
    hash_fpath = os.path.join(cfg.getpath('~/.local/state/fedorafig'),
      f'{hash_name}.sha256')

    with open(hash_fpath, 'w') as fh:
      fh.write(self.checksum)
