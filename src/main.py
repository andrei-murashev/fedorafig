#!/bin/env python3

# IMPORTS ======================================================================
from os import path
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys, cmn, err

def main() -> None:
  # MAIN PARSER ================================================================
  parser_main: ArgumentParser = ArgumentParser(
    formatter_class=RawDescriptionHelpFormatter,
    prog='fedorafig',
    description="CLI utility for Fedora Linux to configure your system from a" \
      " JSON5 file.",
    epilog="Find out more at `https://github.com/andrei-murashev/fedorafig`."
  )

  parser_main.add_argument(
    '-c', '--set-cfg-dir',
    metavar='CFG_DIR',
    type=cmn.set_cfg_dir,
    action='store',
    help="Changes the configuration directory until it is changed again."
  )
  output_types = parser_main.add_mutually_exclusive_group()

  output_types.add_argument(
    '-q', '--quiet',
    action='store_true',
    default=False,
    help="All output is suppressed."
  )

  output_types.add_argument(
    '-v', '--verbose',
    action='store_true',
    default=False,
    help="Shows all subprocesses that are run."
  )

  subparsers = parser_main.add_subparsers(
    title='commands',
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
    type=str,
    action='store',
    help="The configuration file for the utility, tying togetger all \
      configuration assets."
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
    type=str,
    action='store',
    help="The configuration file for the utility, tying togetger all \
      configuration assets."
  )

  parser_run.add_argument(
    '-n', '--no-check',
    action='store_true',
    default=False,
    help="Skips the check if it is otherwise required."
  )

  parser_run.add_argument(
    '-c', '--copies-include',
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
    '-pre', '--prerun-scripts-include',
    action='store_true',
    default=False,
    help="Includes running all prerun scripts before anything else."
  )

  parser_run.add_argument(
    '-post', '--postrun-scripts-include',
    action='store_true',
    default=False,
    help="Includes running all postrun scripts after everything else."
  )

  parser_run.add_argument(
    '-i', '--interactive',
    action='store_true',
    default=False,
    help="Will ask for confirmation when making changes to the file system."
  )

  # BASE PARSER ================================================================
  parser_base = subparsers.add_parser(
    'base',
    help="Checks whether utility configurations are valid."
  )
  parser_base.set_defaults(func=base)
  parser_opts = parser_base.add_mutually_exclusive_group()

  parser_opts.add_argument(
    '-c', '--create',
    action='store',
    help="Saves a list of all currently-installed packages in a file, whose \
      name is the succeeding argument."
  )

  parser_opts.add_argument(
    '-r', '--restore',
    action='store',
    help="Installs and removes necessary packages to ensure that only the \
      packages specified in the file, whose name is the succeeding argument."
  )

  # EXEC PARSER ================================================================
  parser_exec = subparsers.add_parser(
    'exec',
    help="Runs commonly-used scripts stored in the `common` folder, in the \
      utility configuration folder."
  )
  parser_exec.set_defaults(func=exec)

  parser_exec.add_argument(
    'SCRIPT_NAME',
    type=str,
    action='store',
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
  try: args: cmn.ArgsDict = vars(parser_main.parse_args())
  # except err.FedorafigExc: raise
  # except Exception as e: raise err.LogExc(e)
  except SystemExit as e:
    if e.code == 0: return
    raise err.FedorafigExc("Incorrect usage", exc=e)

  if not any(opt for opt in [val for key, val in args.items() if key not in
    ['quiet', 'verbose']]): raise err.FedorafigExc("No arguments")

  if args['quiet']:
    from os import devnull; import sys; cmn.QUIET = True
    with open(devnull, 'w') as fh: sys.stdout = fh; sys.stderr = fh
  elif args['verbose']: cmn.VERBOSE = True

  if 'func' in args and args['func'] is not None:
    from typing import Callable
    if callable(args['func']): func: Callable = args['func'];
    func(args)

# MATCH SUBPARSERS =============================================================
def check(args: cmn.ArgsDict) -> None:
  from check import check; check(args)
  # try: check(args)
  # except err.FedorafigExc: raise
  # except (Exception, SystemExit) as e: raise err.LogExc(e)

def run(args: cmn.ArgsDict) -> None:
  from run import run; run(args)
  # try: run(args)
  # except err.FedorafigExc: pass
  # except (Exception, SystemExit) as e: raise err.LogExc(e)

def base(args: cmn.ArgsDict) -> None:
  from base import create, restore
  if args['create']: create(args['create'])
  elif args['restore']: restore(args['restore'])

def exec(args: cmn.ArgsDict) -> None:
  fpath: str = path.join(cmn.COMMON_PATH, str(args['SCRIPT_NAME']))
  if not path.isfile(fpath): raise err.FedorafigExc(
    "script not found", fpath)
  cmn.shell('chmod u+x', fpath); cmn.shell(fpath)

# UNINSTALLATION ===============================================================
def uninstall(args: cmn.ArgsDict) -> None:
  apaths: list[str] = [cmn.PROG_DIR, path.join(cmn.EXEC_DIR, 'fedorafig')]
  if args['with_state']:
    if path.isdir(cmn.STATE_DIR): apaths.append(cmn.STATE_DIR)
  if args['with_config']:
    if path.isdir(cmn.CFG.path): apaths.append(cmn.CFG.path)

  print("Removing the following paths:")
  for apath in apaths:
    print(' ', apath)
  ans: str = input("Are you sure you want to proceed? [y/N]: ")
  if ans == 'Y' or ans == 'y':
    for apath in apaths: cmn.shell('rm -rf', apath)

# ENTRY POINT ==================================================================
if __name__ == '__main__':
  try: main()
  except KeyboardInterrupt: exit(130)
