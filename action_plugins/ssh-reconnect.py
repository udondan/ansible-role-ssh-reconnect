from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_text
import subprocess
import re
import os
import shlex

class ActionModule(ActionBase):

    TRANSFERS_FILES = False

    def _conn_opt(self, name):
        # prefer the connection plugin's resolved option, fall back to the play context
        # for connection plugins or Ansible versions that don't define it
        try:
            return self._connection.get_option(name)
        except Exception:
            return getattr(self._play_context, name, None)

    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = dict()

        if "all" in self._task.args:
            all = self._task.args.get("all")
            if all == "True" or all == "true" or all == "Yes" or all == "yes": # oh dear
                all = True
        else:
            all = False

        if "user" in self._task.args:
            user = self._task.args.get("user")
        else:
            user = False

        command = "ps -ef | grep -vn ' grep ' | %s | awk '{print \"sudo -n kill -9\", $2}' | sh"

        if user != False:
          grep = "grep sshd | grep '%s'" % user
          command +=  " && echo OTHERUSER"
        elif all == True:
          grep = "grep sshd:"
        else:
          grep = "grep sshd: | grep `whoami`"

        command +=  " && exit"

        target = self._connection.host
        if self._play_context.remote_user:
            target = "%s@%s" % (self._play_context.remote_user, target)

        ssh_cmd = ["ssh", '-tt', '-n', '-S', 'none']

        port = self._conn_opt('port')
        if port:
            ssh_cmd += ['-p', str(port)]

        private_key_file = self._conn_opt('private_key_file')
        if private_key_file:
            ssh_cmd += ['-i', os.path.expanduser(private_key_file)]

        # ssh_args is skipped on purpose, its ControlMaster defaults clash with -S none
        for name in ('ssh_common_args', 'ssh_extra_args'):
            args = self._conn_opt(name)
            if args:
                ssh_cmd += shlex.split(args)

        ssh_cmd += [target, command % grep]

        sub = subprocess.Popen(ssh_cmd,
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        out, err = sub.communicate()
        out = to_text(out, errors='surrogate_or_strict')
        err = to_text(err, errors='surrogate_or_strict')

        os.system('stty sane')

        result = super(ActionModule, self).run(tmp, task_vars)

        if "Write failed: Broken pipe" in err or "Shared connection to" in err or "Connection to %s closed by remote host" % self._connection.host in err or "OTHERUSER" in out:
            result['failed'] = False
        else:
            result['failed'] = True
            result['msg'] = err

        return result
