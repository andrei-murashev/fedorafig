# System packages
import os
import json
import glob
import subprocess

# Local packages
import cfg
from check import Check


class Run():
  def __init__(self, arg_list):
    self.args = vars(arg_list)
    self.data = None
    with open(os.path.join(cfg.CFG_DIR, self.args['CFG_FILE']), 'r') as fh:
      self.data = json.load(fh)

    # Check checksum
    checksum = Check.calc_checksum(self.args['CFG_FILE'])
    checksum_old = ''
    checksum_path = os.path.join(cfg.getpath('~/.local/state/fedorafig/'),
      f'{self.args['CFG_FILE']}.sha256')

    if os.path.exists(checksum_path):
      with open(cfg.getpath(checksum_path), 'r') as fh:
        checksum_old = fh.readline().strip()
    else:
      subprocess.run(['fedorafig', 'check', self.args['CFG_FILE']], check=True)

    if checksum != checksum_old:
      subprocess.run(['fedorafig', 'check', self.args['CFG_FILE']], check=True)
    
    # Parse flags
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
    print('repos_do')
    for key, entry in self.data.items():
      if key == '__COMMENT':
        continue

      repos = []
      print(entry, type(entry))
      for subkey, subentry in entry.items():
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
    print('files_do')
    for key, entry in self.data.items():
      if key == '_COMMENT':
        continue

      syspath = ''
      cfgpath = ''
      for subkey, subentry in entry.items():
        if subkey == 'syspath':
          syspath = cfg.getpath(subentry)
        elif subkey == 'cfgpath':
          cfgpath = os.path.join(cfg.CFG_DIR, 'configs')
          cfgpath = os.path.join(cfgpath, subentry)
          if os.path.isdir(cfgpath):
            cfgpath = os.path.join(cfgpath, '.')

      if not cfgpath:
        continue
      elif not os.path.exists(cfgpath):
        raise RunException(f"File not found: {cfgpath}")

      print("SYSPATH:", syspath, "CFGPATH:", cfgpath)
      subprocess.run(['cp', '-rf', f'{cfgpath}', syspath], check=True)

  
  def __scripts_do(self):
    pass
