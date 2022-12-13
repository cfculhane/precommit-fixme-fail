#!/usr/bin/env python3
# An hook script to verify changes to be committed do not contain
# any 'FIXME:' comments. Called by "git commit" with no arguments.
#
# The hook should exit with non-zero status after issuing an appropriate
# message if it stops the commit.
#
# To bypass this hook, use the "--no-verify" parameter when committing.

# Based on https://github.com/pre-commit/pre-commit-hooks/blob/main/pre_commit_hooks/no_commit_to_branch.py

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from typing import Sequence, Union, Optional, Dict, Tuple, List, AbstractSet

# Define colors
RED = '\033[0;31m'
NC = '\033[0m'


def run_cmd(
        cmd: Union[str, List[str]],
        cwd: Optional[Union[Path, str]] = None,
        extra_env: Dict = None,
        capture_output=False,
        text=True,
        timeout=None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Runs a cmd and returns its output, allowing the capturing of output and specifying a new environment vars for the
    command to run in.
    :param cmd: Either a string cmd for shell, or a list of args to be run outside of a shell
    :param cwd: Working directory of the process, else will be run in the ROOT_DIR
    :param extra_env: Dict of extra env to add to the subprocess
    :param capture_output:  If true, will capture output and store it at p.stdout / p.stderr
    :param text: If true, stdout/stderr will be returned as strings rather than bytes
    :param timeout: Time in seconds to wait before raising TimeoutExpired
    :returns Tuple of (stdout, stderr) if capture_output is True, else (None, None)
    :raises CalledCommandError: If command does not complete with exit code == 0
    """
    shell = True if isinstance(cmd, str) else False

    if isinstance(cwd, Path):
        cwd = str(cwd.absolute())

    if extra_env:
        updated_env = os.environ.copy()
        updated_env.update(extra_env)

    p = subprocess.run(
        cmd, shell=shell, cwd=cwd, env=extra_env, check=False, capture_output=capture_output, text=text, timeout=timeout
    )
    if p.returncode != 0:
        raise CalledProcessError(returncode=p.returncode, cmd=cmd, output=p.stdout, stderr=p.stderr)
    if capture_output:
        return p.stdout.rstrip(), p.stderr.rstrip()
    else:
        return None, None


def is_on_branch(protected: AbstractSet[str]) -> bool:
    try:
        ref_name, _ = run_cmd("git symbolic-ref HEAD", capture_output=True)
    except CalledProcessError:
        return False
    chunks = ref_name.strip().split('/')
    branch_name = '/'.join(chunks[2:])
    return branch_name in protected


def has_fixme_comments():
    matches, _ = run_cmd(r'git diff --cached | grep -iE "\+.*?FIXME" || true', capture_output=True)
    if matches != "":
        print(f"{RED}Error: Found FIXME in attempted commit. \n"
              f"Please remove all occurrences of FIXME before committing.{NC}\n")
        print(matches)
        return True
    else:
        return False


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-b', '--branch', action='append',
        help='branch to disallow commits to, may be specified multiple times',
    )
    args = parser.parse_args(argv)

    protected = frozenset(args.branch or ('master', 'main'))
    if is_on_branch(protected) and has_fixme_comments():
        return 1
    else:
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
