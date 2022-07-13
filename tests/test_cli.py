# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
import shlex
from pathlib import Path
from helper import shell_process

"""Moneo CLI test"""


class CLITestCase(unittest.TestCase):
    """CLI unit test Class."""
    
    def load_data(self,filepath):
        """Helper Function for loading file"""
        data=None
        with Path(filepath).open() as fp:
            data = fp.read()
        return data
        
    def test_cli_args(self):
        """Test bad cli input"""
        cmd="python3 ../moneo.py "
        test_cases=[
            '', #noArg
            '-h', #help
            '-d full -s full', # deploy and shutdown
            'sdaad', #unrecognized input
            '-d notTheRightOption', #bad choice for deploy
            '-s notTheRightOption', #bad choice for shutdown
            '-s full -c /tmp/thisfiledoesnotexist.txt' #unrecognized config
        ]
        
        testFiles=[
            'data/cliHelp.txt',
            'data/cliHelp.txt',
            'data/cliDeployShutdownArgs.txt',
            'data/cliIncorrectDSoption.txt',
            'data/cliIncorrectDSoption.txt',
            'data/cliBadHostfile.txt',
        ]
        
        #test 1 no arg
        testData = self.load_data(testFiles[0])
        args = shlex.split(cmd + test_cases[0])
        result = shell_process.shell_cmd(args)
        assert(result == testData)
        
        #test 2 help ///wrong
        args = shlex.split(cmd + test_cases[1])
        result = shell_process.shell_cmd(args)
        assert(result == testData)
        
        #test 3 deploy and shutdown simultaneously
        testData ='deploy and shutdown are exclusive arguments. Please only provide one.'
        args = shlex.split(cmd + test_cases[2])
        result = shell_process.shell_cmd(args)
        assert(testData in result)
        
        #test 4 unrecognized input
        testData ='error: unrecognized arguments'
        args = shlex.split(cmd + test_cases[3])
        result = shell_process.shell_cmd(args)
        assert(testData in result)
        
        #test 5/6 deploy/shutdown wrong option
        testData ='invalid choice'
        args = shlex.split(cmd + test_cases[4])#deploy
        result = shell_process.shell_cmd(args)
        assert(testData in result)
        args = shlex.split(cmd + test_cases[5])#shutdown
        result = shell_process.shell_cmd(args)
        assert(testData in result)
        
        #test 7 incorrect host config file path
        testData ='does not exist. Please provide a host file.'
        args = shlex.split(cmd + test_cases[6])
        result = shell_process.shell_cmd(args)
        assert(testData in result)
        
if __name__ == '__main__':
    unittest.main()