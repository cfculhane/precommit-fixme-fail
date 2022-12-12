#!/bin/sh
# An hook script to verify changes to be committed do not contain
# any 'FIXME:' comments. Called by "git commit" with no arguments.
#
# The hook should exit with non-zero status after issuing an appropriate
# message if it stops the commit.
#
# To bypass this hook, use the "--no-verify" parameter when committing.

# Redirect output to stderr.
exec 1>&2

# Define colors
RED='\033[0;31m'
NC='\033[0m'

matches=$(git diff --cached | grep -iE '\+.*?FIXME')

if [ "$matches" != "" ]; then
  printf "${RED}Error:${NC} Found FIXME in attempted commit.\n"
  printf "Please remove all occurrences of FIXME before committing.\n"
  printf "  ${matches}\n"
  exit 1
fi
