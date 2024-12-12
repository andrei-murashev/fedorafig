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

    # TODO: Ask for sudo activation at the very start and renew it when needed.
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
      self.__repos_do()
      self.__pkgs_do()
      self.__files_do()
      self.__scripts_do()
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
    repos = []
    for key, entry in self.data.items():
      if key == '_COMMENT':
        continue

      found_repo = False
      found_pkg = False
      cur_subentry = ''
      for subkey, subentry in entry.items():
        if subkey == 'repo' and subentry:
          found_repo = True
          cur_subentry = subentry
        if subkey == 'pkg':
          found_pkg = True
      
      if not found_pkg and found_repo:
        repos.append(cur_subentry)
      
    for repo in repos:
      if repo == 'all':
        path = os.path.join(cfg.CFG_DIR, 'repos', '.')
        subprocess.run(['sudo', 'cp', '-rf', path, '/etc/yum.repos.d/'], 
          check=True)
        break

      path = os.path.join(cfg.CFG_DIR, 'repos', f'{repo}.repo')
      subprocess.run(['sudo', 'cp', '-f', path, '/etc/yum.repos.d/'], check=True)

    try:
      subprocess.run(['dnf', 'repolist'], check=True,
        stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
      raise CheckException(e.stderr.strip())


  def __pkgs_do(self):
    print('pkgs_do')
    done_repos = False
    for key, entry in self.data.items():
      if key == '_COMMENT':
        continue

      repo = ''
      pkg = ''
      for subkey, subentry in entry.items():
        if subkey == 'pkg' and subentry:
          pkg = subentry
        if subkey == 'repo':
          repo = subentry

      if pkg and not repo:
        if not done_repos:
          done_repos = True
          self.__repos_do()
        subprocess.run(['sudo', 'dnf', 'install', pkg, '-y'], check=True)
      elif pkg and repo:
        subprocess.run(['sudo', 'dnf', 'install', f'--enablerepo={repo}',
          f'--setopt=reposdir={cfg.CFG_DIR}/repos/', pkg, '-y'], check=True)


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

      subprocess.run(['cp', '-rf', f'{cfgpath}', syspath], check=True)

  
  def __scripts_do(self):
    print('scripts_do')
    scripts = []
    for key, entry in self.data.items():
      if key == '_COMMENT':
        continue

      script = ''
      for subkey, subentry in entry.items():
        if subkey == 'script':
          path = os.path.join(cfg.CFG_DIR, 'scripts', subentry)
          scripts.append(path)
      
    print(scripts)
    if scripts:
      for script in scripts:
        subprocess.run(['sudo', 'chmod', 'u+x', script], check=True)
        subprocess.run(['sudo', script], check=True)
