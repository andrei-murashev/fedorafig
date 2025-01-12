# fedorafig v0.5.1-alpha
<img
  alt="version static badge"
  src="https://img.shields.io/badge/version-0.5.1-blue"
  height=25>
<img
  alt="unlicense license static badge"
  src="https://img.shields.io/badge/license-Unlicense-red"
  height="25">
<img
  alt="issues static badge"
  src="https://img.shields.io/github/issues/andrei-murashev/fedorafig?color=yellow"
  height="25">
<img
  alt="stars"
  src="https://img.shields.io/github/stars/andrei-murashev/fedorafig?color=white"
  height="25">

Have you ever had to go through the tedious task of writing your own
configuration scripts for your Fedora Linux system? I have, and I didn't like
it, which is why I made this utility for myself and perhaps it can help you too.
`fedorafig` is a one-stop shop configuration utility for Fedora Linux. All you
have to do is specify the configuration paths and their destinations, specify
the packages, optionally from a specific repository, and any post-installation
scripts.

## Installation
In a directory where the path `fedorafig` does not yet exist, execute the following commands
```bash
git clone https://github.com/andrei-murashev/fedorafig
cd fedorafig && chmod u+x install.sh && ./install.sh
cd .. && rm -rf fedorafig
```


## Quick guide
This is a guide on how to use the utility with concrete examples.
### Directory structure
Ensure that the configuration directory, typically `~/.config/fedorafig/` and
referred to as `CFG_DIR`, looks like this:
```bash
~/.config/fedorafig
├── common                      # Holds commonly-used scripts.
│   ├── hi.sh
│   └── ...
├── copies                      # Holds files you want to copy somewhere else.
│   ├── neofetch
│   │   └── config.conf
│   └── ...
├── repos                       # Contains .repo files.
│   ├── fedora.repo
│   ├── fedora-updates.repo
│   └── ...
└── scripts                     # Contains scripts to be run by fedorafig.
    ├── hello.sh
    └── ...
```

### Configuration file
The following example should give you a good idea of how to write your configuration files. The `fedorafig` argument for the name of your file is `CFG_FILE`.
```json5
{
  // Run scripts before and after config application
  work_CLIs: {
    prerun_scripts: ['hello.sh'],
    postrun_scripts: ['bye.sh'],
    repos: ['*'],

    pkgs: [
      'git',
      'tmux',
      'htop',
    ],
  },

  // With copying configuration files for neofetch and lolcat.
  fun_CLIs: {
    postrun_scripts: ['neofetch.sh'],

    copies: [
      ['neofetch/.', '~/.config/neofetch/.'],
      ['lolcat-wrapper.sh', '~/.local/bin/lolcat-wrapper'],
    ],

    pkgs: [
      'neofetch',
      'cmatrix',
      'lolcat',
    ],
  },

  // Installs package, temporarily enabled repos.
  comms: {
    repos: ['rpmfusion-free'],
    pkgs: ['telegram-desktop'],
  },
  
  // Permanently enables repos
  just_repos: {
    repos: ['rpmfusion-free-updates', 'rpmsphere-caution']
  },
}
```
### Using `fedorafig`
Examples: `fedorafig check cfg.json5`, `sudo fedorafig -v run cfg.json5 -r -p` \
Options:
+ `-c CFG_DIR`, `--set-cfg-dir CFG_DIR`     — Changes the configuration
                                            directory until it is changed again.
+ `-q`, `--quiet`               — All output is suppressed.
+ `-v`, `--verbose`             — Shows shells commands for all subprocesses
                                that are run.
Note: `CFG_DIR` is where `fedorafig` searches for you configuration file.

Commands:
+ `check`       — Checks whether utility configurations are valid.
+ `run`         — Applies all configurations to your system through the
                utility. When a flag is provided nothing is initially
                applied, but if a flag is used, a part of the configuration
                specified by the flag will be applied.
+ `exec`        — Runs commonly-used scripts stored in the `common` folder, in
                the utility configuration folder.
+ `uninstall`   — Uninstalls the utility for you.

### Using `fedorafig check`
Examples: `fedorafig check cfg.json5`, `fedorafig check cfg.json5 -c -s` \
Options:
+ `-k`, `--keep-checksums`  — Keeps all old checksums, which are usually
                            deleted.
+ `-c`, `--only-checksum`   — Only calculates the checksum of `CFG_FILE`
                            and saves it.
+ `-s`, `--show-checksum`   — Shows checksum of `CFG_FILE` after it is
                            calculated.
+ `-n`, `--no-checksum`     — Skips calculating the checksum of `CFG_FILE`.
+ `-i`, `--interactive`     — Will ask for confirmation when making changes to
                            the file system.

### Using `fedorafig run`
Examples: `fedorafig run cfg.json5`, `fedorafig run cfg.json5 -i -p -post` \
Options:
+ `-c`, `--copies-include`  — Includes the application of all file transfers.
+ `-p`, `--pkgs-include`    — Includes the application of all package
                            installations.
+ `-r`, `--repos-include`   — Includes the application of all specified
                            repository enabling.
+ `-pre`, `--prerun-scripts-include`
                    — Includes running all prerun scripts before anything else.
+ `-post`, `--postrun-scripts-include`
                    — Includes running all postrun scripts after everything
                    else.
+ `-i`, `--interactive`     — Will ask for confirmation when making changes to
                            the file system.

### Using `fedorafig base`
Example: `fedorafig base -c cur_pkgs.txt`, 
`sudo fedorafig base --restore old_pkgs.txt` \
Options:
+ `-c`, `--create`          — Saves a list of all currently-installed packages
                            in a file, whose name is the succeeding argument.
+ `-r`, `--restore`         — Installs and removes necessary packages to ensure
                            that only the packages specified in the file, whose
                            name is the succeeding argument, are installed.

### Using `fedorafig exec`
Example: `fedorafig exec hi.sh`, `sudo fedorafig exec hi.sh` \
Note: There are no options, and `fedorafig` is to be run with `sudo` to execute
the script with elevated privileges.

### Using `fedorafig uninstall`
Example: `fedorafig uninstall`, `sudo fedorafig uninstall -s -c` \
Options:
+ `-s`, `--with-state`      — Also delete the state directory while
                            uninstalling.
+ `-c`, `--with-config`     — Also delete the configuration directory while
                            uninstalling.
