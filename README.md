# ssh reconnect

The `ssh-reconnect` role provides two handlers you can use in your roles:

 - `Kill own ssh connections`: Kills all open ssh connections of the current user
 - `Kill all ssh connections`: Kills all open ssh connections of any user

Before you can use the handlers you need to add the role to your playbook or as a dependency in your own role. Then simply notify one of the handlers:

```yml
 - some_task:
   notify:
     - Kill own ssh connections
```

There also is a module (or better action-plugin) you can use to directly kill ssh-connections without a handler.

## Parameters

 - `user`: Name of the user whose ssh connections should be killed
 - `all`: Set to `True` if all ssh connections of all users should be killed

By default (when none of the parameters is set) all ssh connections of the user you connect as will be killed.

## Connection

The action plugin opens its own ssh connection from the controller instead of reusing Ansible's. It passes these connection variables to `ssh`:

 - `ansible_host` and `ansible_user`
 - `ansible_port`
 - `ansible_ssh_private_key_file`
 - `ansible_ssh_common_args` and `ansible_ssh_extra_args`

Anything else, such as `ansible_ssh_args`, is not used and comes from your `~/.ssh/config`. Password authentication (`ansible_ssh_pass`) is not supported. Killing the sessions requires passwordless `sudo` on the target.


## Examples

Kill own ssh connections:
```yml
- name: Kill own ssh connections
  ssh-reconnect:
```

Kill all ssh connections:
```yml
- name: Kill all ssh connections
  ssh-reconnect: all=True
```

Kill ssh connections of user foo
```yml
- name: Kill all ssh connections of user foo
  ssh-reconnect: user=foo
```
