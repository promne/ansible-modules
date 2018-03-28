#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Jiri George Holy <george@h01y.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import re
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'supported_by': 'community',
    'status': ['preview', 'deprecated']
}

DOCUMENTATION = '''
---
module: jboss_cli_deploy
short_description: deploy applications to JBoss
description:
  - Deploy applications to JBoss using the CLI
options:
  deployment:
    required: true
    description:
      - The name of the deployment
  src:
    required: true
    description:
      - The remote path of the application ear or war to deploy
  cli_path:
    required: true
    description:
      - Path to jboss-cli.sh
  host:
    required: false
    default: localhost
    description:
      - Host of target JBoss instance
  port:
    required: false
    default: 9999
    description:
      - Port binding for management API
  user:
    required: false
    default: admin
    description:
      - Username for JBoss management user
  password:
    required: false
    default: admin
    description:
      - Password for JBoss management user
author: Jiri George Holy (@promne)      
'''

EXAMPLES = '''
# Deploy a hello world application
- jboss_cli_deploy:
    deployment: hello.war
    src: /tmp/hello-1.0-SNAPSHOT.war
    cli_path: /opt/jboss-as/bin/jboss-cli.sh
    host: 192.168.0.5
    user: admin
    password: seceret
    
'''

def is_deployed(module):
    rc, stdout, stderr = cli_run_commands(module, ['/deployment=%s:read-resource' % module.params['deployment']])
    if rc == 0:
        try:
            checksum = ''.join(re.search('bytes \{(.+?)\}', stdout, re.DOTALL).group(1).split()).replace('0x', '').replace(',', '')
                                    
            if module.sha1(module.params['src']) == checksum:
                return True
        except AttributeError:
            return False            
    return False


def cli_deploy(module, deployed):
    if deployed:
        return False
    rc, stdout, stderr = cli_run_commands(module, ['deploy --name=%s %s --force' % (module.params['deployment'], module.params['src'])])
    if rc == 0:
        return True
    else:
        module.fail_json(msg=stderr)


def cli_run_commands(module, commands):
    return module.run_command([
        module.params['cli_path'],
        '--connect',
        '--controller=%s:%d' % (module.params['host'], module.params['port']),
        '--user=%s' % module.params['user'],
        '--password=%s' % module.params['password'],
        '--commands=%s' % ','.join(commands)
    ])


def main():

    module = AnsibleModule(
        argument_spec=dict(
            deployment=dict(required=True),
            src=dict(type='path', required=True),
            cli_path=dict(type='path', required=True),
            host=dict(default='localhost'),
            port=dict(type='int', default=9999),
            user=dict(default='admin'),
            password=dict(default='admin')
        )
    )
    
    deployed = is_deployed(module)
    result = dict(changed=cli_deploy(module, deployed))
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()

