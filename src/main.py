#!/bin/env python3

# System imports
import os
import argparse

# Local imports
import cfg
import help
import errors


def main():
  """============================ MAIN PARSER ============================="""
  parser_main = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    prog='fedorafig',
    description="CLI utility for Fedora Linux to configure your system from a JSON file.",
    epilog="Find out more at `https://github.com/andrei-murashev/fedorafig`."
  )

  parser_main.add_argument(
    '-c', '--set-cfg-dir',
    type=cfg.set_cfg_dir,
    action='store',
    help="Changes the configuration directory."
  )

  parser_main.add_argument(
    '-q', '--quiet',
    action='store_true',
    default=False,
    help="All output is suppressed."
  )

  parser_main.add_argument(
    '-v', '--verbose',
    action='store_true',
    default=False,
    help="Reports more concrete processes."
  )

  subparsers = parser_main.add_subparsers(
    title='commands',
    description=""
  )

  """============================ CHECK PARSER ============================"""
  parser_check = subparsers.add_parser(
    'check',
    help="Checks whether utility configurations are valid."
  )
  parser_check.set_defaults(func=check)

  parser_check.add_argument(
    'CFG_FILE',
    action='store',
    default=None,
    help="The configuration file for the utility tying all configuration assets."
  )

  parser_check.add_argument(
    '-k', '--keep-checksums',
    action='store_true', 
    default=False,
    help="Keeps all old checksums, which are usually deleted."
  )
  
  parser_check.add_argument(
    '-c', '--only-checksum',
    action='store_true',
    default=False,
    help="Only calculates the checksum of CFG_FILE and saves it."
  )

  parser_check.add_argument(
    '-s', '--show-checksum',
    action='store_true',
    default=False,
    help="Shows checksum of CFG_FILE after it is calculated."
  )

  parser_check.add_argument(
    '-n', '--no-checksum',
    action='store_true',
    default=False,
    help="Skips calculating the checksum of CFG_FILE."
  )

  """============================= RUN PARSER ============================="""
  parser_run = subparsers.add_parser(
    'run',
    help="Applies all configurations to your system through the utility. \
      When a flag is provided nothing is initially applied, but if a flag is used, a part of the configuration specified by the flag will be applied."
  )
  parser_run.set_defaults(func=run)

  parser_run.add_argument(
    'CFG_FILE',
    action='store',
    default=None,
    help="The configuration file for the utility tying all configuration assets."
  )

  parser_run.add_argument(
    '-f', '--files-include',
    action='store_true',
    default=False,
    help="Includes the application of all file transfers."
  )

  parser_run.add_argument(
    '-p', '--pkgs-include',
    action='store_true',
    default=False,
    help="Includes the application of all package installations."
  )

  parser_run.add_argument(
    '-r', '--repos-include',
    action='store_true',
    default=False,
    help="Includes the application of all specified repository enabling."
  )

  parser_run.add_argument(
    '-s', '--scripts-include',
    action='store_true',
    default=False,
    help="Includes the running of all scripts at the end."
  )

  """============================= EXEC PARSER ============================"""
  parser_exec = subparsers.add_parser(
    'exec',
    help="Runs commonlu-used scripts stored in the `common` folder, in the \
      utility configuration folder."
  )
  parser_exec.set_defaults(func=exec)

  parser_exec.add_argument(
    'SCRIPT_NAME',
    action='store',
    default=None,
    help="The name of the script you wish to run."
  )

  """========================== UNINSTALL PARSER =========================="""
  parser_uninstall = subparsers.add_parser(
    'uninstall',
    help="Uninstalls the utility for you."
  )
  parser_uninstall.set_defaults(func=uninstall)

  parser_uninstall.add_argument(
    '-s', '--with-state',
    action='store_true',
    default=False,
    help="Also delete the state directory while uninstalling."
  )

  parser_uninstall.add_argument(
    '-c', '--with-config',
    action='store_true',
    default=False,
    help="Also delete the configuration directory while uninstalling."
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


def exec(args):
  name = args['SCRIPT_NAME']
  path = os.path.join(cfg.COMMON_DIR, name)
  if not os.path.isfile(path): raise errors.FedorafigException(
    "script not found", path)
  
  from subprocess import run, CalledProcessError
  run(['chmod', 'u+x', path], check=True)
  try: run([path], check=True)
  except CalledProcessError as e: print(e)


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
