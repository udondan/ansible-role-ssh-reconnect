from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
import subprocess
import re
import os

class ActionModule(ActionBase):
    
    TRANSFERS_FILES = False
    
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
        
        sub = subprocess.Popen(["ssh", '-tt', '-n', '-S', 'none', self._connection.host, command % grep],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        
        out, err = sub.communicate()
        
        os.system('stty sane')        
        
        result = super(ActionModule, self).run(tmp, task_vars)
        
        if "Write failed: Broken pipe" in err or "Shared connection to" in err or "Connection to %s closed by remote host" % self._connection.host in err or "OTHERUSER" in out:
            result['failed'] = False
        else:
            result['failed'] = True
            result['msg'] = err
        
        return result
