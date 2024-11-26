import argparse


# TODO: Check professionalism
class MultiArgumentError(Exception):
  def __init__(self, *args):
    self.args = args
    self.msg = f"Found arguments incompatible together: {', '.join(args)}"
  
  def __str__(self):
    if self.args == None:
      return self.msg[:index(':')]
    else:
      return self.msg


def enforce_mutually_exclusive_groups(args, group1, group2):
  args1 = [action.dest for action in group1._group_actions]
  args2 = [action.dest for action in group2._group_actions]
  print("ARGS:", args1, args2)
  for arg1 in args1:
    for arg2 in args2:
      if getattr(args, arg1) != None and getattr(args, arg2) != None:
        raise MultiArgumentError(arg1, arg2)


def main(*args, **kwargs):
  parser = argparse.ArgumentParser(
    prog='fedorafig',
    description=
      "CLI utility for Fedora Linux to configure your system \
      from a JSON file.",
    epilog=
      "Find this project and its documentation at GitHub: \
      https://github.com/amura-dev/fedorafig"
  )
  subparsers = parser.add_subparsers()

  parser_check = subparsers.add_parser('check')
  parser_check.add_argument('-k', '--keep-checksums')

  no_checksum = parser_check.add_argument_group('no checksum')
  no_checksum.add_argument('-n', '--no-checksum')

  yes_checksum = parser_check.add_argument_group('yes checksum')
  yes_checksum.add_argument('-c', '--only-checksum')
  yes_checksum.add_argument('-s', '--show-checksum')

  args = parser.parse_args()
  enforce_mutually_exclusive_groups(args, yes_checksum, no_checksum)
  print(args)


if __name__ == '__main__':
  main()
