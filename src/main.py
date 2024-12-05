#!/bin/env python3

# TODO: Write tests for everything
# System packages
import os
import argparse
import textwrap
import fileinput

# Local packages
import cfg
from check import Check


class MyArgumentParser(argparse.ArgumentParser):
  parser_map = {}
  mutually_excluded_groups = {}

  def __init__(self, prog=None, *args, **kwargs):
    super().__init__(prog, *args, **kwargs)

    if prog in self.__class__.parser_map.keys():
      raise Exception(f'Parser already exists for: {prog}')
    elif prog == None:
      return

    self.name = prog
    self.__class__.parser_map[self.name] = self


  def error(self, msg):
    super().error(textwrap.dedent(f"""
      {msg}
      Try '{self.name} --help' for more information.
    """).strip())
    exit(2)


  @staticmethod
  def custom_error(name, msg):
    print(textwrap.dedent(f"""
      {name}: error: {msg}
      Try '{name} --help' for more information.
    """).strip())
    exit(2)

  
  def mutually_exclude_groups(self, *argparse_groups):
    grouped_flags = []
    for group in argparse_groups:
      flags = [action.dest for action in group._group_actions]
      grouped_flags.append(flags)
    self.__class__.mutually_excluded_groups[self.name] = grouped_flags
  

  def parse_args(self, *args, **kwargs):
    # `self.name` is different here, as we are using the top-level parser
    args = super().parse_args(*args, **kwargs)
    supergroups = self.mutually_excluded_groups

    for parser_name, groups in supergroups.items():
      matches = []
      for group in groups:
        try: vals = [getattr(args, flag) for flag in group]
        except AttributeError: return args
        matches.append(self.__list_disjunction(vals))
      
      collision_found = self.__list_conjunction(matches)
      if collision_found:
        # TODO: format the error message to display the flags
        msg = 'arguments from mutually exclusive groups were used:'
        self.__class__.parser_map[parser_name].error(msg)
    
    return args


  @staticmethod
  def __list_disjunction(xs):
    ret = False
    for x in xs:
      ret = ret or x
    
    return ret


  @staticmethod
  def __list_conjunction(xs):
    ret = True
    for x in xs:
      ret = ret and x
    
    return ret



# TODO: Add examples, write help prompts
def main():
  parser = MyArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    prog='fedorafig',
    description=textwrap.dedent("""
      CLI utility for Fedora Linux to configure your system from a JSON file.
    """.strip()),
    epilog=textwrap.dedent("""\
    Find this project and its documentation on GitHub at:
    https://github.com/amura-dev/fedorafig
    """.strip())
  )

  parser.add_argument(
    '-f', '--set-cfg-dir',
    type=set_cfg_dir,
    help='set the config dir to something, and it will be this until set again'
  )

  subparsers = parser.add_subparsers(
    title='commands',
    description="Main commands of the utility."
  )

  parser_check = subparsers.add_parser(
    'check',
    usage='%(prog)s [-h] [-k] [-c, -s | -n] CFG_DIR'
  )

  yes_checksum = parser_check.add_argument_group('Use checksum')
  no_checksum = parser_check.add_argument_group('Ignore checksum')
  parser_check.set_defaults(func=check)

  parser_check.add_argument(
    'CFG_DIR',
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


  parser_check.mutually_exclude_groups(yes_checksum, no_checksum)
  """
  Group exclusion must be triggered after groups are initialised.
  For changes to be reflected after adding arguments to group,
  the mutual exclusion method must be called again.
  """

  args = parser.parse_args()
  '''
  if not hasattr(args, 'func'):
    parser.error('No command specified')

  if not args
    parser.error("No flags or arguments given")
  '''
  no_option = True
  for val in vars(args).values():
    if val != None:
      no_option = False
      break

  if no_option:
    parser.error("No arguments were provided")


  try: args.func(args)
  except AttributeError: pass


def set_cfg_dir(arg):
  fpath = os.path.abspath(arg)
  if not(os.path.exists(fpath) and os.path.isdir(fpath)):
    MyArgumentParser().custom_error('fedorafig',
      f'argument -f/--set-cfg-dir: path does not exist or is not a \
      directory: {fpath}'.replace('  ', ''))

  for line in fileinput.input('cfg.py', inplace=True):
    if line.startswith('cfg_dir_path ='):
      line_new = f"cfg_dir_path = '{fpath}'"
      print(line_new)
    else:
      print(line, end='')


def check(args):
  print('check reached')
  Check(args)


if __name__ == '__main__':
  main()
