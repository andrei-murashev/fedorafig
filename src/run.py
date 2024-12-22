# DEPENDENCY: dnf-plugins-core

# System imports
import os
import json
import threading
import subprocess

# Local imports
import cfg
import errors

class Run():
  def __init__(self, args):
    try: subprocess.run(['sudo', '-v'], check=True)
    except subprocess.CalledProcessError as e: raise errors.FedorafigException(
      "sudo timeout")
    sudo_refresh = threading.Thread(target=cfg.sudo_refresh, daemon=True)
    sudo_refresh.start()

    self.args = args
    self.file = args['CFG_FILE']
    self.repos_done = False

    with open(os.path.join(cfg.CFG_DIR, self.file), 'r') as fh:
      self.data = json.load(fh)

    from check import Check
    self.checksum = Check.calc_checksum(self.file)

    # Compare checksums
    checksum_old = None
    checksum_path = os.path.join(cfg.STATE_DIR, f'{self.file}.sha256')

    if os.path.isfile(checksum_path):
      with open(checksum_path, 'r') as fh: checksum_old = fh.readline().strip()

    if not (os.path.isfile(checksum_path) and self.checksum == checksum_old):
      subprocess.run(['fedorafig', 'check', self.file], check=True)

    Check(args)

    # Parse flags
    flags = [
      self.args['repos_include'],
      self.args['pkgs_include'],
      self.args['files_include'],
      self.args['scripts_include']
    ]

    print("Applying configurations")
    if True not in flags:
      self.__repos_do()
      self.__pkgs_do()
      self.__files_do()
      self.__scripts_do()
    if self.args['repos_include']: self.__repos_do()
    if self.args['pkgs_include']: self.__pkgs_do()
    if self.args['files_include']: self.__files_do()
    if self.args['scripts_include']: self.__scripts_do()


  def __repos_do(self):
    repo_files = os.path.join(cfg.REPOS_DIR, '.')
    try: subprocess.run(['dnf', 'config-manager', '--version'], check=True)
    except subprocess.CalledProcessError: raise errors.FedorafigException(
      "'config-manager' not found or has an issue")
    subprocess.run(
      ['sudo', 'cp', '-rf', repo_files, '/etc/yum.repos.d/'], check=True)

    enable_all = False
    for repo, pkg in cfg.REPOS_N_PKGS:
      if repo == 'all' and not pkg: enable_all = True; break
      elif repo and not pkg: subprocess.run([
        'sudo', 'dnf', 'config-manager', '--set-enabled', repo], check=True)

    if enable_all:
      repos_cmd = ['--set-enabled']
      for repo, pkg in cfg.REPOS_N_PKGS:
        if repo == 'all': print("Enabling all repos"); continue
        elif repo and not pkg: repos_cmd += [repo]
      subprocess.run(['sudo', 'dnf', 'config-manager', *repos_cmd], check=True)

    self.repos_done = True


  def __pkgs_do(self):
    if not self.repos_done: self.__repos_do()
    for repo, pkg in cfg.REPOS_N_PKGS:
      if repo == 'all' and pkg:
        print(f"Temporarily enabling all repositories to install {pkg}")
        subprocess.run(
          ['sudo', 'dnf', 'install', '--enablerepo=*', pkg, '-y'], check=True)
      elif repo and pkg:
        print(f"Temporarily enabling repository {repo} to install {pkg}")
        subprocess.run(
          ['sudo', 'dnf', 'install', f'--enablerepo={repo}', pkg, '-y'],
          check=True)
        # NOTE: This does not disable other repos.
      elif pkg and not repo:
        print(f"Installing {pkg}")
        subprocess.run(['sudo', 'dnf', 'install', pkg, '-y'], check=True)


  def __files_do(self):
    for syspath, cfgpath in cfg.SYS_N_CFG_DIRS:
      cfgpath_items = os.path.join(cfgpath, '.')
      print(f"Copying {cfgpath_items} to {syspath}")
      subprocess.run(['sudo', 'cp', '-rf', cfgpath_items, syspath], check=True)


  def __scripts_do(self):
    for script in cfg.SCRIPT_FILES:
      print(f"Running script {script}")
      subprocess.run(['sudo', 'chmod', 'u+x', script], check=True)
      subprocess.run(['sudo', script], check=True)
