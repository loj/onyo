#!/usr/bin/env python3

import logging
import os
import sys

from git import Repo

from onyo.utils import (
    build_git_add_cmd,
    run_cmd,
    edit_file
)

logging.basicConfig()
logger = logging.getLogger('onyo')


def build_commit_cmd(files, onyo_root):
    return ["git -C \"" + onyo_root + "\" commit -m", "edit asset(s).\n\n" + "\n".join(files)]


def prepare_arguments(sources, onyo_root):
    problem_str = ""
    list_of_sources = []
    if isinstance(sources, str):
        sources = ["".join(sources)]
    for source in sources:
        current_source = source
        if not os.path.isfile(current_source):
            current_source = os.path.join(onyo_root, source)
        if not os.path.exists(current_source):
            problem_str = problem_str + "\n" + current_source + " does not exist."
        # check if file is in git
        run_output = run_cmd("git -C \"" + onyo_root + "\" ls-tree -r HEAD ")
        if source not in run_output:
            problem_str = problem_str + "\n" + current_source + " is not in onyo."
        else:
            list_of_sources.append(current_source)
    if problem_str != "":
        logger.error(problem_str)
        sys.exit(1)
    return list(dict.fromkeys(list_of_sources))


def edit(args, onyo_root):
    """
    Open the ``asset`` file(s) using the default text editor specified by the
    environment variable ``EDITOR`` (``nano`` and then ``vi`` are used as
    fallbacks).

    When multiple asset files are given, Onyo will open them in sequence.

    After editing an ``asset``, ``onyo`` will check the validity of the YAML
    syntax and check if the changed file still follows the rules specified in
    ``.onyo/validation/validation.yaml``, and if problems are found it gives the
    choice to either correct them or discard the changes to make sure that the
    repository stays in a valid state.
    """

    # do not run onyo fsck! Onyo should allow to correct problems with onyo
    # edit, and after editing onyo checks the syntax and validates the updated
    # file anyways, so new problems can't be introduced, but old ones can be
    # corrected.
    # check and set paths
    list_of_sources = prepare_arguments(args.asset, onyo_root)
    # iterate over file list, edit them, add changes
    for source in list_of_sources:
        git_filepath = os.path.relpath(source, onyo_root)
        # change file
        edit_file(source, onyo_root)
        # check if changes happened and add them
        repo = Repo(onyo_root)
        changed_files = [item.a_path for item in repo.index.diff(None)]
        if len(changed_files) != 0:
            git_add_cmd = build_git_add_cmd(onyo_root, git_filepath)
            run_cmd(git_add_cmd)
    # commit changes
    [commit_cmd, commit_msg] = build_commit_cmd(changed_files, onyo_root)
    run_cmd(commit_cmd, commit_msg)
