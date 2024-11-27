# System packages
import itertools

# External packages
# import pytest

# Local packages
from ..src.main import enforce_mutually_exclusive_groups


parameters = []

arg_dict = {
  'keep_checksums': False,
  'only_checksum': False,
  'no_checksum': False,
  'show_checksum': False
}

values = list(itertools.product([None, False, True], repeat=len(arg_dict)))

for value in values:
  args = dict(zip(arg_dict.keys(), value))
  status = (args['keep_checksums'] or args['only_checksum'] or \
    args['show_checksum']) and not args['no_checksum']
  parameters.append((arg_dict, status))

'''
@pytest.mark.parametrize("arg_dict, status", parameters)
def test_enforce_mutually_exclusive_groups(arg_dict, status):
  pass
'''
