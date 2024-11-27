# System packages
import json

# Local packages
import cfg


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
    pass

  def __check_syntax(self):
    pass

  def __calc_checksum(self):
    pass
