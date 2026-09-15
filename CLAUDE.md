# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An Ansible Galaxy role (`ssh-reconnect`) that kills open sshd sessions on the target host. This makes Ansible open a fresh connection on the next task, for example after changing group membership or login settings. The role has no tasks. It provides handlers and an action plugin that other roles use as a dependency.

There is no build system, linter, test suite, or CI. You can only verify changes by running a playbook against a real host that includes this role (for example via `roles_path` or as a role dependency).

## Architecture

- `action_plugins/ssh-reconnect.py`: all the logic. It runs **on the controller**, not on the target:
  - It builds a shell pipeline (`ps -ef | grep sshd... | awk ... sudo -n kill -9 PID | sh`) and runs it by starting a separate local `ssh -tt -n -S none [<remote_user>@]<host>` subprocess. It deliberately bypasses Ansible's connection plugin (`-S none` avoids the ControlMaster socket, so it does not kill its own multiplexed connection).
  - Only `self._connection.host` is passed, prefixed with `self._play_context.remote_user@` when a remote user is set (it can be `None`, so keep the guard). Ansible's port, key and other connection vars are **not** used, so the call relies on the controller's `~/.ssh/config` and defaults for those.
  - Success is detected **inverted**: the remote shell dying is the expected outcome. The task counts as successful when stderr contains `Write failed: Broken pipe`, `Shared connection to`, or `Connection to <host> closed by remote host`, or when stdout contains the `OTHERUSER` marker (set when killing another user's sessions, where our own connection survives). Anything else marks the task as failed and puts stderr in `msg`.
  - It calls `stty sane` locally afterwards to repair the controller terminal after `-tt`.
  - Arguments: `user=<name>` (matched with `grep sshd | grep '<name>'`), `all=True` (matches `sshd:`; only the strings `True/true/Yes/yes` count as true), and no args (sessions of `whoami` on the remote). `user` takes precedence over `all`. Killing requires passwordless `sudo -n` on the target.
  - The code is Python 2 style (`__metaclass__ = type`, str checks on the bytes output of `communicate()`). Keep this in mind when you touch it: under Python 3 the `in err` checks need decoding.
- `library/ssh-reconnect`: an empty module stub. Ansible needs a module file with the same name for the action plugin to be callable as a task (`ssh-reconnect:`). Don't delete it.
- `handlers/main.yml`: two handlers, `Kill own ssh connections` and `Kill all ssh connections`, that wrap the action plugin. Their names are the public API (consumers `notify` them), so renaming them breaks users.
- `meta/main.yml`: Galaxy metadata. `dependencies` is defined once via a YAML anchor inside `galaxy_info` and aliased at top level.
- `README.md`: user-facing docs for handlers, parameters and examples. Keep it in sync when you change arguments or handler names.

The role and plugin name uses a hyphen (`ssh-reconnect`), not an underscore. It was renamed from underscore, and the README, handlers and plugin/module filenames must all match.
