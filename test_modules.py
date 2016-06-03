#!/usr/bin/env python
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager


def install_os(playbook_vars, image):
    args = {
        'host': '{{ inventory_hostname }}',
        'username': '{{ username }}',
        'password': '{{ password }}',
        'platform': 'cisco_nxos_nxapi',
        'system_image_file': image,
    }

    play_source =  dict(
        name = "Install OS {0}".format(image),
        hosts = 'nxos',
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module='ntc_install_os', args=args))
        ]
      )
    play = Play().load(play_source, variable_manager=playbook_vars['variable_manager'], loader=playbook_vars['loader'])

    # actually run it
    tqm = None
    try:
        tqm = TaskQueueManager(
                  inventory=playbook_vars['inventory'],
                  variable_manager=playbook_vars['variable_manager'],
                  loader=playbook_vars['loader'],
                  options=playbook_vars['options'],
                  passwords=playbook_vars['passwords'],
                  stdout_callback='default',
              )
        result = tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()


def run_playbook(playbook_vars, nxos_images, base_image, upgrade):

    for image in nxos_images:
	if upgrade and image != base_image:
            install_os(playbook_vars, image)

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
	
	"""
	failed = False
	if pb._failed_hosts.values():
            failed = True
	"""
	
	if upgrade is False:
	    break

    # restore base image
    if upgrade:
        install_os(playbook_vars, base_image)

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
    group_vars = variable_manager._group_vars_files['nxos'][0]
    upgrade = group_vars['upgrade']
    nxos_images = group_vars['images']['nxos']
    base_image = group_vars['images']['base_image']

    playbook_vars = {
        'inventory': inventory,
        'variable_manager': variable_manager,
        'loader': loader,
        'options': options,
        'passwords': passwords
    }

    pb = run_playbook(playbook_vars, nxos_images, base_image, upgrade)



if __name__ == '__main__':
    main()
