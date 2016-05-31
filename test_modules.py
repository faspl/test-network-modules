#!/usr/bin/env python
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor


def run_playbook(playbook_vars):
    pb = PlaybookExecutor(
          playbooks=['./nxos.yaml'],
          inventory=playbook_vars['inventory'],
          variable_manager=playbook_vars['variable_manager'],
          loader=playbook_vars['loader'],
          options=playbook_vars['options'],
          passwords=playbook_vars['passwords'],
        )

    pb.run()
    pb = pb._tqm

    return pb

def main():
    inventory_file = 'hosts'

    variable_manager = VariableManager()
    loader = DataLoader()
    Options = namedtuple('Options',
                        ['connection',
                         'forks',
                         'become',
                         'become_method',
                         'become_user',
                         'check',
                         'listhosts',
                         'listtasks',
                         'listtags',
                         'syntax',
                         'module_path'
                         ])

    options = Options(connection='local', forks=100, become=None,
                      become_method=None, become_user=None, check=False,
                      listhosts=False, listtasks=False, listtags=False,
                      syntax=False, module_path="")

    nxos_module = dict(limit_to='nxos_module')
    passwords = dict(vault_pass='secret')

    inventory = Inventory(loader=loader, variable_manager=variable_manager,
                          host_list=inventory_file)

    variable_manager.set_inventory(inventory)
    variable_manager._extra_vars.update(nxos_module)

    playbook_vars = {
        'inventory': inventory,
        'variable_manager': variable_manager,
        'loader': loader,
        'options': options,
        'passwords': passwords
    }

    failed = False
    pb = run_playbook(playbook_vars)

    if pb._failed_hosts.values():
        failed = True


if __name__ == '__main__':
    main()
