from typing import *

subentries: Dict[str, List[List[str]]] = {
  'prerun_scripts': [['pre1.sh', 'pre2.sh', 'pre3.sh'],     ['NONE'], ['EMPTY']],
  'postrun_scripts': [['post1.sh', 'post2.sh', 'post3.sh'], ['NONE'], ['EMPTY']],
  'repos': [['rpmsphere', 'copr', 'fedora-cisco-openh256'], ['NONE'], ['EMPTY']],
  'pkgs': [['git', 'cmatrix', 'neofetch'],                  ['NONE'], ['EMPTY']],
}

special_subentries: Dict[str, List[List[str]]] = {
  'prerun_scripts': [['pre1.sh', 'pre2.sh', 'pre3.sh'],     ['NONE'], ['EMPTY']],
  'postrun_scripts': [['post1.sh', 'post2.sh', 'post3.sh'], ['NONE'], ['EMPTY']],
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
cfg_dicts: List[Dict[str, Optional[List[str]]]] = []
for cfg_dict in proto_cfg_dicts:
  tmp_dict: Dict[str, Optional[List[str]]] = {}
  for key in cfg_dict.keys():
    if cfg_dict[key] == ['NONE']: tmp_dict[key] = None
    elif cfg_dict[key] != ['EMPTY']: tmp_dict[key] = cfg_dict[key]
  cfg_dicts.append(tmp_dict)

from json5 import dump; num: int = 0
for cfg_dict in cfg_dicts:
  with open(f'cfg_{num}.json5', 'w') as fh: dump(cfg_dict, fh, indent=2)
  num += 1
