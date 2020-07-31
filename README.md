# ansible-vars-plugin-layered
Ansible vars_plugin to pull vars from a hiera-like hierarchy

## What does it do?

This plugin adds in variables based on the environment + groups your hosts belong to. It will load variables from ./vars/`env`/`group`.yaml, where `env` is 'dev', 'stage', or 'prod', and `group` is any other group the hosts belong to.
  
## How does it work?

The plugin searches the host's groups for a group named `dev`, `stage`, or `prod` and attempts to load files that are named after the remaining groups in ./vars/`env`/`group`.yaml.
  
A host belonging to groups `prod`, `web`, and `monitor` will try to load ./vars/prod/web.yaml and ./vars/prod/monitor.yaml.

## What does this solve?

One of the big problems I see with ansible is the way that variables are handled. A good infrastructure has 2-3 environments for each of its services. Typically, you would have 'dev', 'stage', and 'prod' environments for each service that you configure. On top of that, you separate configurations by their function. Maybe you have databases, webservers, a network-filesystem cluster, and load-balancers, each of these setup in multiple environments. 

A typical split-env inventory for this scenario would look like so:

```ini
# prod inventory
[prod:children]
webservers
databases
loadbalancers
nfs

[webservers]
prod-web[1:5]

[databases]
prod-db[1:3]

[loadbalancers]
prod-lb[1:2]

[nfs]
prod-nfs[1:2]

# stage inventory
[stage:children]
webservers
databases
loadbalancers
nfs

[webservers]
stage-web[1:2]

[databases]
stage-db[1:2]

[loadbalancers]
stage-lb[1:2]

[nfs]
stage-nfs[1:2]

# dev inventory
[dev:children]
webservers
databases
loadbalancers
nfs

[webservers]
dev-web1

[databases]
dev-db1

[loadbalancers]
dev-lb1

[nfs]
dev-nfs1
```

You probably want to configure the db in dev to have a different configuration than stage or prod. How do you do this easily with this inventory structure? Sure, you could create a group that combines the env with the service, such as `dev-databases` and `stage-databases`, but this will lead to a massive, painful-to-maintain, and bug-laden inventory. More importantly, Ansible's variable precedence works in alphabetical order, so variable definitions might get overridden, such as a default config in `webservers` could override a more specific definition in `prod-webservers`. This plugin solves these problems.
