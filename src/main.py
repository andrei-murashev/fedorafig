# TODO: Write tests for everthing
# System packages
import inspect
import argparse
import textwrap
import itertools

# Local packages
import cfg
from check import Check


class MyArgumentParser(argparse.ArgumentParser):
  parser_map = {}
  mutually_excluded_groups = {}

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.name = kwargs['prog']
    self.__class__.parser_map[self.name] = self


  def error(self, msg):
    super().error(textwrap.dedent(f"""
      {msg}
      Try '{self.name} --help' for more information.
    """).strip())
    print(exit_msg, end='')
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
        matches.append(self.list_disjunction(vals))
      
      collision_found = self.list_conjunction(matches)
      if collision_found:
        # TODO: format the error message to display the flags
        msg = 'arguments from mutually exclusive groups were used:'
        self.__class__.parser_map[parser_name].error(msg)
    
    return args



  @staticmethod
  def list_disjunction(xs):
    ret = False
    for x in xs:
      ret = ret or x
    
    return ret


  @staticmethod
  def list_conjunction(xs):
    ret = True
    for x in xs:
      ret = ret and x
    
    return ret



# TODO: Add examples.
def main(*args, **kwargs):
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
  if not hasattr(args, 'func'):
    parser.error('No command specified')
  args.func(args)


def check(args):
  print('check reached')
  pass


if __name__ == '__main__':
  main()
