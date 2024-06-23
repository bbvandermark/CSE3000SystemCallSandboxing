This repository contains code and data related to my bachelor's thesis, titled "An analysis of system call set extraction tools on configurable Linux binaries".
The repository contains the following files and directories:
- `busybox_configs`: All `.config` files used to compile busybox.
- `confine_scripts`: All scripts used as an entry point in the Docker containers used by the analysis of Confine.
- `results`: Raw results acquired by running the analysis scripts
- `secret`: Should contain a public and private key such that the sysfilter git repository can be cloned. This key should be known to both GitHub and GitLab.
- `targets`: Contains all binaries that were analysed.
- `binalyzer.docker` - Dockerfile which builds a Docker image that runs Binalyzer on all binaries in `targets`
- `confine_runner.py` - Python script that runs Confine on all binaries in `targets`
- `process_results.py` - Python script which performs analysis on the acquired results
- `results.json` - JSON containing the analysis done by `process_results.py`
- `run_all.sh` - shell script that runs all commands required to run Binalyzer, Sysfilter and Confine
- `sourcealyzer.docker` - Dockerfile which attempts to build a Docker image that runs Sourcealyzer. Does not work, but is included for completeness.
- `sysfilter.docker` - Dockerfile which builds a Docker image that runs Sysfilter on all binaries in `targets`
