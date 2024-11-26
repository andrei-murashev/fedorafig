import pytest
from src.main import Main


parameters = []
@pytest.mark.parametrize("args_dict, status", parameters)
def test_enforce_mutually_exclusive_groups(args_dict, status):
  pass
