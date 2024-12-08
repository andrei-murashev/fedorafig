# System packages
import json
import glob
import subprocess


class RunException(Exception):
  """Exception that lets `argparse` know that it should exit with an error,
  instead of `python3`, and traceback will be shown."""
  pass



class Run():
  def __init__(self, arg_list):
    self.args = vars(arg_list)
    self.data = None
    with open(os.path.join(cfg.CFG_DIR, self.args['CFG_FILE'], 'r')) as fh:
      self.data = json.load(fh)

    # TODO: Implement checksum comparison.
    
    if not self.args:
      self.__all_do()

    if self.args['repos_include']:
      self.__repos_do()

    if self.args['pkgs_include']:
      self.__pkgs_do()

    if self.args['files_include']:
      self.__files_do()

    if self.args['scripts_include']:
      self.__scripts_do()


  def __repos_do(self):
    for key, entry in self.data.items():
      if key == '__COMMENT':
        continue

      repos = []
      if subkey, subentry in entry.items():
        if subkey == 'repo':
          repos.append(subentry)

      for repo in repos:
        if repo == 'all':
          repo_paths = os.path.join(cfg.CFG_DIR, 'repos/*')
          for path in glob.glob(repo_paths):
            if os.path.isfile(path):
              subprocess.run(['cp', path, '/tmp/fedorafig_repos'], check=True)
          break

        path = os.path.join(cfg.CFG_DIR, 'repos', f'{repo}.repo')
        subprocess.run(['cp', path, '/etc/yum.repos.d/'], check=True)

    try:
      subprocess.run(['dnf', 'repolist'], check=True,
        stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
      raise CheckException(e.stderr.strip())


  def __pkgs_do(self):
    pass


  def __files_do(self):
    for key, entry in self.data.items():
      if key == '_COMMENT':
        continue

      syspath = ''
      cfgpath = os.path.join(cfg.CFG_DIR, 'configs')
      for subkey, subentry in entry.items():
        if subkey == 'syspath':
          syspath = subentry
        elif subkey == 'cfgpath':
          cfgpath = os.path.join(cfgpath, subentry)

      subprocess.run(['cp', cfgpath, syspath], check=True)

  
  def __scripts_do(self):
    pass
