# System packages
import argparse
import textwrap

# Local packages
import cfg
from check import Check


# TODO: Check professionalism
class MultiArgumentError(Exception):
  def __init__(self, *args):
    self.args = ['--' + arg.replace('_', '-') for arg in args]
    self.msg = f"Found flags incompatible together: {', '.join(self.args)}"
  
  def __str__(self):
    if self.args == None:
      return self.msg[:index(':')]
    else:
      return self.msg



# TODO: Write test for:
def enforce_mutually_exclusive_groups(arg_list, group1, group2):
  flags1 = [action.dest for action in group1._group_actions]
  flags2 = [action.dest for action in group2._group_actions]
  for flag1 in flags1:
    for flag2 in flags2:
      arg1 = getattr(arg_list, flag1)
      arg2 = getattr(arg_list, flag2)
      if arg1 and arg2:
        raise MultiArgumentError(flag1, flag2)


# TODO: Add examples.
def main(*args, **kwargs):
  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    prog='fedorafig',
    description=textwrap.dedent("""
      CLI utility for Fedora Linux to configure your system
      from a JSON file
    """.replace('\n', ' ')),
    epilog=textwrap.dedent("""
    Find this project and its documentation on GitHub at:
    https://github.com/amura-dev/fedorafig
    """)
  )

  subparsers = parser.add_subparsers(
    title='commands',
    description="Main commands of the utility."
  )

  parser_check = subparsers.add_parser('check')
  yes_checksum = parser_check.add_argument_group('Calculating checksum')
  no_checksum = parser_check.add_argument_group('Not calculating checksum')

  parser_check.add_argument(
    'cfg_dir',
    help=f'System configuration directory in {cfg.CFG_DIR}'
  )

  parser_check.add_argument(
    '-k', '--keep-checksums',
    action='store_true', 
    default=False,
    help='something'
  )

  yes_checksum.add_argument(
    '-c',
    '--only-checksum',
    action='store_true',
    default=False
  )

  yes_checksum.add_argument(
    '-s',
    '--show-checksum',
    action='store_true',
    default=False
  )

  no_checksum.add_argument(
    '-n',
    '--no-checksum',
    action='store_true',
    default=False
  )

  arg_list = parser.parse_args()
  enforce_mutually_exclusive_groups(arg_list, yes_checksum, no_checksum)
  Check(vars(arg_list))


if __name__ == '__main__':
  main()
