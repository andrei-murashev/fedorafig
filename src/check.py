# System packages
import os
import glob
import json

# Local packages
import cfg
import errors


class Check():
  def __init__(self, arg_list):
    self.args = vars(arg_list)
    self.checksum = ''
    print(self.args)

    if not self.args['keep_checksums']: self.__delete_checksums()
    if not self.args['only_checksum']: self.__check_syntax()
    if not self.args['no_checksum']: self.__calc_checksum()
    if self.args['show_checksum']: print(f"{cfg.CFG_DIR} checksum: {self.checksum}")


  def __delete_checksums(self):
    state_dir = os.path.abspath('~/.local/state/fedorafig')
    try:
      os.makedirs(state_dir, exists_ok=True)
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
    pass


  def __calc_checksum(self):
    pass
