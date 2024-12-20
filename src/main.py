#!/bin/env python3

# System imports
import os
import argparse

# Local imports
import cfg
import help
import errors

# TODO: Check setting of configuration directory and __repos_do(),
# if it sets the repos_done flag


def main():
  """============================ MAIN PARSER ============================="""
  parser_main = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    prog='fedorafig',
    description="", # TODO
    epilog="" # TODO
  )

  parser_main.add_argument(
    '-c', '--set-cfg-dir',
    type=cfg.set_cfg_dir,
    # default='~/.config/fedorafig',
    help="" # TODO
  )

  subparsers = parser_main.add_subparsers(
    title='', # TODO
    description="" # TODO
  )

  """============================ CHECK PARSER ============================"""
  parser_check = subparsers.add_parser(
    'check',
    usage='', # TODO
    help="" # TODO
  )
  parser_check.set_defaults(func=check)

  parser_check.add_argument(
    'CFG_FILE',
    help="" # TODO
  )

  parser_check.add_argument(
    '-k', '--keep-checksums',
    action='store_true', 
    default=False,
    help="" # TODO
  )
  
  parser_check.add_argument(
    '-c', '--only-checksum',
    action='store_true',
    default=False,
    help="" # TODO
  )

  parser_check.add_argument(
    '-s', '--show-checksum',
    action='store_true',
    default=False,
    help="" # TODO
  )

  parser_check.add_argument(
    '-n', '--no-checksum',
    action='store_true',
    default=False,
    help="" # TODO
  )

  """============================= RUN PARSER ============================="""
  parser_run = subparsers.add_parser(
    'run',
    usage='', # TODO
    help="" # TODO
  )
  parser_run.set_defaults(func=run)

  parser_run.add_argument(
    'CFG_FILE',
    help="" # TODO
  )

  parser_run.add_argument(
    '-f', '--files-include',
    action='store_true',
    default=False,
    help="" # TODO
  )

  parser_run.add_argument(
    '-p', '--pkgs-include',
    action='store_true',
    default=False,
    help="" # TODO
  )

  parser_run.add_argument(
    '-r', '--repos-include',
    action='store_true',
    default=False,
    help="" # TODO
  )

  parser_run.add_argument(
    '-s', '--scripts-include',
    action='store_true',
    default=False,
    help="" # TODO
  )

  """========================== UNINSTALL PARSER =========================="""
  parser_uninstall = subparsers.add_parser(
    'uninstall',
    usage='', # TODO
    help="" # TODO
  )
  parser_uninstall.set_defaults(func=uninstall)

  parser_uninstall.add_argument(
    '-s', '--with-state',
    action='store_true',
    default=False,
    help="" # TODO
  )

  parser_uninstall.add_argument(
    '-c', '--with-config',
    action='store_true',
    default=False,
    help="" # TODO
  )

  """============================= PARSE OPTS ============================="""
  try:
    args = vars(parser_main.parse_args())
  except errors.FedorafigException as e:
    raise
  except SystemExit as e:
    if e.code == 0: return
    raise errors.FedorafigException("Incorrect usage", exc=e)
  except Exception as e:
    errors.log(e); print(help.REPORT_ISSUE)

  if not any(opt is not None for opt in args.values()):
    raise errors.FedorafigException("No arguments")
  
  if 'func' in args and args['func'] is not None: args['func'](args)


def check(args):
  from check import Check
  try: Check(args)
  except errors.FedorafigException as e: raise
  except (Exception, SystemExit) as e: errors.log(e); print(help.REPORT_ISSUE)


def run(args):
  from run import Run
  try: Run(args)
  except errors.FedorafigException as e: raise
  except (Exception, SystemExit) as e: errors.log(e); print(help.REPORT_ISSUE)


def uninstall(args):
  from subprocess import run

  paths = [cfg.PROG_DIR, os.path.join(cfg.EXEC_DIR, 'fedorafig')]
  if args['with_state']:
    if os.path.isdir(cfg.STATE_DIR): paths.append(cfg.STATE_DIR)
  if args['with_config']:
    if os.path.isdir(cfg.CFG_DIR): paths.append(cfg.CFG_DIR)

  print("Removing the following paths:")
  for path in paths:
    print(' ', path)

  ans = input("Are you sure you want to proceed [y/N]: ")
  if ans == 'Y' or ans == 'y':
    for path in paths: run(['rm', '-rf', path], check=True)


if __name__ == '__main__':
  main()
