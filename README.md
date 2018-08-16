# OpenSPARKL CLI
[OpenSPARKL Project Home](http://opensparkl.org)

Console CLI interface for managing running SPARKL nodes.

Get the latest from [releases](/releases).

# Build
Choose python or python3 by setting the `PYTHON_VERSION` env var, then use `make` as follows:

1. `export PYTHON_VERSION=3` (assuming you want to use Python3, default is 2).
2. `make deps` to set up dependencies.
3. `make rel` to create distribution in `dist` directory.
4. `make install` to install. Use `sudo -H make install` if necessary.

# Run
Use `sparkl -h` to see help as follows:

```
usage: sparkl_cli [-h] [-v] [-a ALIAS] [-s SESSION] [-t TIMEOUT]
                  {active,call,cd,close,connect,elastic,listen,login,logout,ls,mkdir,node,object,put,render,rm,service,session,source,start,stop,undo,vars}
                  ...

SPARKL command line utility.

positional arguments:
  {active,call,cd,close,connect,elastic,listen,login,logout,ls,mkdir,node,object,put,render,rm,service,session,source,start,stop,undo,vars}
    active              list active services
    call                invoke a transaction or individual operation
    cd                  show or change current folder
    close               close connection
    connect             create or show connections
    elastic             push JSON to Elasticsearch
    listen              listen for events on any configuration object
    login               login user or show current login
    logout              logout user
    ls                  list content of folder or service
    mkdir               create new folder
    node                show node info (administrator only)
    object              get object JSON by name or id
    put                 upload XML source [or change] file
    render              transform source configuration or local file into html
    rm                  remove object
    service             start service implementation module
    session             show current session info
    source              view [and download] source configuration
    start               start a service
    stop                stop one or more services
    undo                undo last change
    vars                set field variables

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -a ALIAS, --alias ALIAS
                        optional alias for multiple connections
  -s SESSION, --session SESSION
                        optional session id, defaults to invoking pid
  -t TIMEOUT, --timeout TIMEOUT
                        request timeout in seconds, default 0 means no timeout

Use 'sparkl_cli <cmd> -h' for subcommand help

```

# Uninstall
* To remove a global installation:
  ```bash
  sudo -H pip[3] uninstall sparkl_cli
  ```
* To remove a user installation:
  ```
  pip[3] uninstall sparkl_cli
  ```