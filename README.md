ssh reconnect
=============================

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

###Parameters

 - `user`: Name of the user whose ssh connections should be killed
 - `all`: Set to `True` if all ssh connections of all users should be killed

By default (when none of the parameters is set) all ssh connections of the user you connect as will be killed.


###Examples

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
