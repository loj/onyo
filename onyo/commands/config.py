#!/usr/bin/env python3

import logging
import os

from onyo.utils import (
    run_cmd,
    get_git_root,
    build_git_add_cmd
)
from onyo.commands.fsck import read_only_fsck

logging.basicConfig()
logger = logging.getLogger('onyo')


def build_commit_cmd(command, onyo_root):
    return ["git -C \"" + onyo_root + "\" commit -m", "update .onyo/config\n\n" + command]


def build_command(key, onyo_root):
    cmd_str = ""
    for arg in key:
        if " " in arg:
            cmd_str += " \"" + arg + "\""
        else:
            cmd_str += " " + arg
    return " ".join(["git config -f \"" + os.path.join(onyo_root, ".onyo/config") + "\"" + cmd_str])


def config(args, onyo_root):
    """
    Set a ``variable`` to ``value`` in the ``.onyo/config`` file. This command
    can for example change the default tool for the interactive mode of ``onyo
    history`` with ``onyo config history.interactive "git log --follow"``.
    """

    # run onyo fsck
    read_only_fsck(args, onyo_root, quiet=True)
    # build command
    command = build_command(args.key, get_git_root(onyo_root))
    git_add_cmd = build_git_add_cmd(get_git_root(onyo_root), ".onyo/config")
    [commit_cmd, commit_msg] = build_commit_cmd(command, get_git_root(onyo_root))
    # run command
    run_cmd(command)
    run_cmd(git_add_cmd)
    run_cmd(commit_cmd, commit_msg)
