import unittest
from subprocess import Popen, PIPE, STDOUT
import os

def test_generic(test_name):
    p = Popen(['python', 'cpusim.py', "--file", os.path.join("tests", test_name, test_name + ".ass")],
              stdout=PIPE, stdin=PIPE,
              stderr=STDOUT)

    data_in = ""

    if os.path.isfile(os.path.join("tests", test_name, test_name + ".in")):
        with open(os.path.join("tests", test_name, test_name + ".in"), "r") as inf:
            data_in = inf.read()

    cmd_out = p.communicate(input=data_in.encode())[0]
    p.wait()
    expected_out = ""

    with open(os.path.join("tests", test_name, test_name + ".res"), "r") as expectedf:
        expected_out = expectedf.read()

    return cmd_out.decode(), expected_out

class TestSim(unittest.TestCase):
    def setUp(self):
        pass

    def test1(self):
        cmd_out, expected_out = test_generic("test1")
        # print(cmd_out, expected_out)
        self.assertEqual(cmd_out, expected_out)

    def test2(self):
        cmd_out, expected_out = test_generic("test2")
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

    def testsk_no_haz(self):
        cmd_out, expected_out = test_generic("testsk-no-haz")
        self.assertEqual(cmd_out, expected_out)

    def testjmp(self):
        cmd_out, expected_out = test_generic("testjmp")
        self.assertEqual(cmd_out, expected_out)

    def testboolexpr(self):
        cmd_out, expected_out = test_generic("boolexpr")
        self.assertEqual(cmd_out, expected_out)

    def testisort10(self):
        cmd_out, expected_out = test_generic("insertion-sort-10")
        self.assertEqual(cmd_out, expected_out)

    # def testisort100(self):
    #     cmd_out, expected_out = test_generic("insertion-sort-100")
    #     self.assertEqual(cmd_out, expected_out)

    # def testfun10(self):
    #     cmd_out, expected_out = test_generic("functions10")
    #     self.assertEqual(cmd_out, expected_out)

if __name__ == '__main__':
    unittest.main(verbosity=2)
