# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
import shlex
from helper import shell_process
import re
import os

"""Moneo ansible single node test"""


class AnsibleTestCase(unittest.TestCase):
    """Ansible unit test class"""
    

    def check_docker_status(self):
        """Helper to check docker container status"""
        cmd='sudo docker container ls'
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args,15)
        return ('grafana' in result), ( 'prometheus' in result )
   
    def check_exporter_status(self):
        """Helper to check exporter status"""
        cmds=['ps -f -C  python3','ps -f -C  python3']
        expected=['nvidia_exporter.py', 'net_exporter.py']
        
        for i in range(len(cmds)):
            args = shlex.split(cmds[i])
            result = shell_process.shell_cmd(args,15)
            if expected[i] not in result:
                return False
        return True
    
    def test_ansible_good_output(self):
        """Test ansible deployment and shutdown output"""
        path=os.path.dirname(__file__)
        if path:
            path=path + '/'
        cmds = ['ansible-playbook -i ' + path + 'data/host.ini ' + path + '../src/ansible/deploy.yaml',
            'ansible-playbook -i ' + path + 'data/host.ini ' + path + '../src/ansible/shutdown.yaml']          
        expected= ['failed=0','localhost'] #used for correct ansible output
        #test successful deploy and shutdown output
        for i in range(len(cmds)):
            args = shlex.split(cmds[i])
            result = shell_process.shell_cmd(args,120)
            for exp in expected:
                assert(exp in result) #check that ansible output has printed the correct output based on expected
                
    def test_ansible_deployed(self):
        """Test ansible deployed containers/exporters"""
        path=os.path.dirname(__file__)
        if path:
            path=path + '/'
        cmd = 'ansible-playbook -i ' + path + 'data/host.ini ' + path + '../src/ansible/deploy.yaml'        
        #test successful deploy by looking at docker
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args,60)
        print(result)
        #checking docker containers up
        graf_status, prom_status =self.check_docker_status()
        assert(graf_status)
        assert(prom_status)
        #checking exporters launched
        exporter_status=self.check_exporter_status()
        assert(exporter_status)
        
    def test_ansible_shutdown(self):
        """Test ansible shutdown containers/exporters"""
        path=os.path.dirname(__file__)
        if path:
            path=path + '/'        
        cmd = 'ansible-playbook -i ' + path + 'data/host.ini ' + path + '../src/ansible/shutdown.yaml'      
        #test successful deploy by looking at docker
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args,60)
        #checking docker containers down
        graf_status, prom_status =self.check_docker_status()
        self.assertFalse(graf_status)
        self.assertFalse(prom_status)
        #checking exporters killed
        exporter_status=self.check_exporter_status()
        self.assertFalse(exporter_status)
    
    def test_ansible_bad_hostfile(self):
        """Test ansible when give bad input file"""
        path=os.path.dirname(__file__)
        if path:
            path=path + '/'          
        cmd = 'ansible-playbook -i doesnotexist.ini ' + path + '../src/ansible/shutdown.yaml'
        expected=['Unable to parse','no hosts matched']
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args,15)
        assert(expected[0] in result)
        assert(expected[1] in result)

if __name__ == '__main__':   
    unittest.main()
