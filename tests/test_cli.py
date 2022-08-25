# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
import shlex
from helper import shell_process
from helper import file_util
import os
import re
from pathlib import Path
"""Moneo CLI test"""


class CLITestCase(unittest.TestCase):
    """CLI unit test Class."""
        
    def test_cli_args(self):
        """Test bad cli input"""
        
        #change directory to Moneo test directory
        cdir=os.path.dirname(__file__)
        if(cdir):
            os.chdir(cdir)    
            
        cmd="python3 ../moneo.py "
        
        test_cases=[
            '', #noArg
            '-h', #help
            '-d -s', # deploy and shutdown
            '--notTheRightOption', #unrecognized input
            '-d notTheRightOption', #bad choice for deploy
            '-s full -c /tmp/thisfiledoesnotexist.txt' #unrecognized config
        ]

        #test 1 no arg
        testData = 'Moneo CLI Help Menu'
        args = shlex.split(cmd + test_cases[0])
        result = shell_process.shell_cmd(args,15)
        assert(testData in result)
        
        #test 2 help 
        testData = 'Moneo CLI Help Menu'
        args = shlex.split(cmd + test_cases[1])
        result = shell_process.shell_cmd(args,15)
        assert(testData in result)
        
        #test 3 deploy and shutdown simultaneously
        testData ='deploy and shutdown are exclusive arguments. Please only provide one.'
        args = shlex.split(cmd +'-c data/host.ini '+ test_cases[2])
        result = shell_process.shell_cmd(args,15)
        assert(testData in result)
        
        #test 4 unrecognized input
        testData ='error: unrecognized arguments'
        args = shlex.split(cmd + test_cases[3])
        result = shell_process.shell_cmd(args,15)
        assert(testData in result)
        
        #test 5 deploy wrong option
        testData ='Defaulted to the full option.'
        args = shlex.split(cmd + '-c data/host.ini ' + test_cases[4])#deploy
        result = shell_process.shell_cmd(args,60)        
        assert(testData in result)
        
        #test 6 incorrect host config file path
        testData ='does not exist. Please provide a host file.'
        args = shlex.split(cmd + test_cases[5])
        result = shell_process.shell_cmd(args,15)
        assert(testData in result)
 
if __name__ == '__main__':
    unittest.main()
