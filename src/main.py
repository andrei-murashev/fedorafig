#!/bin/env python3

# System imports
from os import path
import argparse

# Local imports
import cmn, err


def main() -> None:
# MAIN PARSER ==================================================================
  parser_main = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    prog='fedorafig',
    description="CLI utility for Fedora Linux to configure your system from a JSON file.",
    epilog="Find out more at `https://github.com/andrei-murashev/fedorafig`."
  )

  parser_main.add_argument(
    '-c', '--set-cfg-dir',
    type=cmn.set_cfg_dir,
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

  # CHECK PARSER ===============================================================
  parser_check = subparsers.add_parser(
    'check',
    usage="usage: fedorafig check [-h] [-k] [-c -s | -n] CFG_FILE",
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

  parser_check.add_argument(
    '-i', '--interactive',
    action='store_true',
    default=False,
    help="Will ask for confirmation when making changes to the file system."
  )

  # RUN PARSER =================================================================
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

  # EXEC PARSER ================================================================
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

  # UNINSTALL PARSER ===========================================================
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

  # PARSE OPTIONS ==============================================================
  try: args: cmn.ArgsDict = \
    vars(parser_main.parse_args())
  except err.FedorafigExc as e: raise
  except Exception as e: raise err.LogExc(e)
  except SystemExit as e:
    if e.code == 0: return
    raise err.FedorafigExc("Incorrect usage", exc=e)

  if not any(opt for opt in args.values()):
    raise err.FedorafigExc("No arguments")
  
  if 'func' in args and args['func'] is not None:
    from typing import Callable
    if callable(args['func']): func: Callable = args['func'];
    func(args)


def check(args: cmn.ArgsDict) -> None:
  from check import Check
  try: Check(args)
  except err.FedorafigExc: raise
  except (Exception, SystemExit) as e: raise err.LogExc(e)


def run(args: cmn.ArgsDict) -> None: pass
'''
  from run import Run
  try: Run(args)
  except err.FedorafigExc: raise
  except (Exception, SystemExit) as e: raise err.LogExc(e)
'''


def exec(args: cmn.ArgsDict) -> None:
  fpath: str = path.join(cmn.COMMON_PATH, str(args['SCRIPT_NAME']))
  if not path.isfile(fpath): raise err.FedorafigExc(
    "script not found", fpath)
  
  from subprocess import run, CalledProcessError, PIPE
  run(['chmod', 'u+x', fpath], check=True)
  try: run([fpath], check=True, stderr=PIPE)
  except CalledProcessError as e: raise err.FedorafigExc(e.stderr.decode())


def uninstall(args: cmn.ArgsDict) -> None:
  from subprocess import run

  apaths: list[str] = [cmn.PROG_DIR, path.join(cmn.EXEC_DIR, 'fedorafig')]
  if args['with_state']:
    if path.isdir(cmn.STATE_DIR): apaths.append(cmn.STATE_DIR)
  if args['with_config']:
    if path.isdir(cmn.CFG.path): apaths.append(cmn.CFG.path)

  print("Removing the following paths:")
  for apath in apaths:
    print(' ', apath)

  ans: str = input("Are you sure you want to proceed [y/N]: ")
  if ans == 'Y' or ans == 'y':
    for apath in apaths: run(['rm', '-rf', apath], check=True)


if __name__ == '__main__':
  main()
