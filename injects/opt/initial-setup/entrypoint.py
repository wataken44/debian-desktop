#!/usr/bin/env python

""" entrypoint.py


"""

import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__)) + "/"
CUSTOMIZE_FILE = BASE_DIR + "customize.txt"


def main():
    configure_logger()
    run_script()


def configure_logger():
    logging.basicConfig(
        filename=BASE_DIR + "entrypoint.log",
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO,
    )


def run_script():
    if not os.path.exists(CUSTOMIZE_FILE):
        logger.error(f"{CUSTOMIZE_FILE} not found")
        return

    fp = open(CUSTOMIZE_FILE)

    for line in fp:
        cmd = line.strip()
        if len(cmd) == 0 or cmd[0] == "#":
            continue
        rc = execute(cmd)
        if rc != 0:
            sys.exit(rc)

    fp.close()


def execute(cmd):
    logger.info(cmd)
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    out = proc.stdout
    if out is not None:
        out = out.strip()

    err = proc.stderr
    if err is not None:
        err = err.strip()

    sep = "\n"
    if (out == "" and err == "") or (out is None and err is None):
        sep = ", "
    logging.info(f"rc: {proc.returncode}{sep}stdout: {out}{sep}stderr: {err}")

    return proc.returncode


if __name__ == "__main__":
    main()
