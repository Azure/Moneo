# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
import shlex
from helper import shell_process
from helper import file_util

"""Moneo CLI test"""


class CLITestCase(unittest.TestCase):
    """CLI unit test Class."""
        
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
        
        #test 1 no arg
        testData = file_util.load_data('data/cliHelp.txt')
        args = shlex.split(cmd + test_cases[0])
        result = shell_process.shell_cmd(args,15)
        assert(result == testData)
        
        #test 2 help ///wrong
        args = shlex.split(cmd + test_cases[1])
        result = shell_process.shell_cmd(args,15)
        assert(result == testData)
        
        #test 3 deploy and shutdown simultaneously
        testData ='deploy and shutdown are exclusive arguments. Please only provide one.'
        args = shlex.split(cmd + test_cases[2])
        result = shell_process.shell_cmd(args,15)
        assert(testData in result)
        
        #test 4 unrecognized input
        testData ='error: unrecognized arguments'
        args = shlex.split(cmd + test_cases[3])
        result = shell_process.shell_cmd(args,15)
        assert(testData in result)
        
        #test 5/6 deploy/shutdown wrong option
        testData ='invalid choice'
        args = shlex.split(cmd + test_cases[4])#deploy
        result = shell_process.shell_cmd(args,15)
        assert(testData in result)
        args = shlex.split(cmd + test_cases[5])#shutdown
        result = shell_process.shell_cmd(args,15)
        assert(testData in result)
        
        #test 7 incorrect host config file path
        testData ='does not exist. Please provide a host file.'
        args = shlex.split(cmd + test_cases[6])
        result = shell_process.shell_cmd(args,15)
        assert(testData in result)
        
if __name__ == '__main__':
    unittest.main()