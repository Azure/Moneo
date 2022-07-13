# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
import shlex
from helper import shell_process
import re

"""Moneo ansible single node test"""


class AnsibleTestCase(unittest.TestCase):
    """Ansible unit test class"""
    
    def check_docker_status(self):
        """Helper to check docker container status"""
        cmd='sudo docker container ls'
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args)
        if ('grafana' in result) or ( 'prometheus' in result ):
            return True #deployed
        else:
            return False #not deployed
            
    def check_exporter_status(self):
        """Helper to check exporter status"""
        cmds=['ps -f -C  python2','ps -f -C  python3']
        expected=['nvidia_exporter.py', 'net_exporter.py']
        ret=False
        for i in range(2):
            args = shlex.split(cmds[i])
            result = shell_process.shell_cmd(args)
            ret = expected[i] in result
        return ret
    
    def test_ansible_good_output(self):
        """Test ansible deployment and shutdown"""
        cmds = ['ansible-playbook -i data/host.ini ../src/ansible/deploy.yaml','ansible-playbook -i data/host.ini ../src/ansible/shutdown.yaml']        
        expected= ['failed=0','localhost'] #used for correct ansible output
        procStatus=[True,False]#used for checking exporter and docker status
        #test 1/2 successful deploy and shutdown output
        for i in range(2):
            args = shlex.split(cmds[i])
            result = shell_process.shell_cmd(args)
            for exp in expected:
                assert(exp in result) #check that ansible output has printed the correct output based on expected
            assert(self.check_exporter_status() == procStatus[i]) #check exporter status
            assert(self.check_docker_status() == procStatus[i])#check docker status
            
       
    
    def test_ansible_bad_hostfile(self):
        """Test ansible when give bad input file"""
        cmd = 'ansible-playbook -i doesnotexist.ini ../src/ansible/shutdown.yaml'
        expected=['Unable to parse','no hosts matched']
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args)
        assert(expected[0] in result)
        assert(expected[1] in result)

if __name__ == '__main__':
    unittest.main()
