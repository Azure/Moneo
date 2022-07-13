# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
import shlex
from helper import shell_process
import re

"""Moneo ansible single node test"""


class AnsibleTestCase(unittest.TestCase):
    """Ansible unit test class"""
    
    def test_ansible_good_output(self):
        cmds = ['ansible-playbook -i data/host.ini ../src/ansible/deploy.yaml','ansible-playbook -i data/host.ini ../src/ansible/shutdown.yaml']        
        expected= ['failed=0','localhost']
        #test 1/2 successful deploy and shutdown output
        for cmd in cmds:
            args = shlex.split(cmd)
            result = shell_process.shell_cmd(args)
            for exp in expected:
                assert(exp in result)
       
    
    def test_ansible_bad_hostfile(self):
        cmd = 'ansible-playbook -i doesnotexist.ini ../src/ansible/shutdown.yaml'
        expected=['Unable to parse','no hosts matched']
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args)
        assert(expected[0] in result)
        assert(expected[1] in result)

if __name__ == '__main__':
    unittest.main()
