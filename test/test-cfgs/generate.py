from typing import *

subentries: Dict[str, List[List[str]]] = {
  'prerun_scripts': [['pre1.sh', 'pre2.sh', 'pre3.sh'],     ['EMPTY']],
  'postrun_scripts': [['post1.sh', 'post2.sh', 'post3.sh'], ['EMPTY']],
  'repos': [['rpmsphere', 'copr:bgstack15:AfterMozilla',
             'fedora-cisco-openh264'], ['EMPTY']],
  'pkgs': [['git', 'cmatrix', 'neofetch'],                  ['EMPTY']],
}

special_subentries: Dict[str, List[List[str]]] = {
  'prerun_scripts': [['pre1.sh', 'pre2.sh', 'pre3.sh'],     ['EMPTY']],
  'postrun_scripts': [['post1.sh', 'post2.sh', 'post3.sh'], ['EMPTY']],
  'pkgs_special': [['telegram-desktop', 'mpv', 'vlc']],
  'repos_special': [['rpmfusion-free', 'fedora', 'update']]
}

from itertools import product
def list_dicts_product(input_dict: Dict[str, List[List[str]]]) \
  -> List[Dict[str, List[str]]]:
    keys = input_dict.keys()
    values = input_dict.values()
    product_combinations = product(*values)
    
    result = []
    for combo in product_combinations:
        result_dict = {key: list(value) for key, value in zip(keys, combo)}
        result.append(result_dict)

    return result

proto_cfg_dicts: List[Dict[str, List[str]]] \
  = list_dicts_product(subentries) + list_dicts_product(special_subentries)
  # NOTE: ^ Could cause issues

cfg_dicts: List[Dict[str, Optional[List[str]]]] = []
for cfg_dict in proto_cfg_dicts:
  tmp_dict: Dict[str, Optional[List[str]]] = {}
  for key in cfg_dict.keys():
    if cfg_dict[key] != ['EMPTY']: tmp_dict[key] = cfg_dict[key]
  cfg_dicts.append(tmp_dict)

from json5 import dump; num: int = 0
for cfg_dict in cfg_dicts:
  with open(f'cfg_{num}.json5', 'w') as fh:
    fh.write('{\n')
    fh.write('  entry: ')
    dump(cfg_dict, fh, indent=4)
    fh.write('}')
  num += 1
