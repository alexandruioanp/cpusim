import unittest
import cpusim
from subprocess import Popen, PIPE, STDOUT
import os

def test_generic(test_name):

    p = Popen(['python', 'cpusim.py', os.path.join("tests", test_name, test_name + ".ass")], stdout=PIPE, stdin=PIPE,
              stderr=STDOUT)

    data_in = ""

    if os.path.isfile(os.path.join("tests", test_name, test_name + ".in")):
        with open(os.path.join("tests", test_name, test_name + ".in"), "r") as inf:
            data_in = inf.read()

    cmd_out = p.communicate(input=data_in)[0]
    expected_out = ""

    with open(os.path.join("tests", test_name, test_name + ".res"), "r") as expectedf:
        expected_out = expectedf.read()

    return cmd_out.decode(), expected_out


class TestSim(unittest.TestCase):
    def setUp(self):
        pass

    def test1(self):
        cmd_out, expected_out = test_generic("test1")
        self.assertEqual(cmd_out, expected_out)

    def test2(self):
        cmd_out, expected_out = test_generic("test2")
        self.assertEqual(cmd_out, expected_out)

    def test3(self):
        cmd_out, expected_out = test_generic("test3")
        self.assertEqual(cmd_out, expected_out)

    def test4(self):
        cmd_out, expected_out = test_generic("test4")
        self.assertEqual(cmd_out, expected_out)

    def test6(self):
        cmd_out, expected_out = test_generic("test6")
        self.assertEqual(cmd_out, expected_out)

    def test7(self):
        cmd_out, expected_out = test_generic("test7")
        self.assertEqual(cmd_out, expected_out)

    def testsk(self):
        cmd_out, expected_out = test_generic("testsk")
        self.assertEqual(cmd_out, expected_out)

if __name__ == '__main__':
    unittest.main()