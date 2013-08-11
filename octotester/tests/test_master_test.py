
import unittest
from octotester.testers import (
    create_formatted_report, TestMaster)
from multiprocessing import Queue



class MasterTest(unittest.TestCase):

    def setUp(self):
    	pass

    def test_master(self):
        changes_queue = Queue()
        changes_queue.put("/home/att/projects/octotester/octotester/tests/test_task_executor.py")
        changes_queue.put("sweets!")
        changes_queue.put("sweets!")
        master = TestMaster(changes_queue, './')
        master.run()


class DisplayResultTest(unittest.TestCase):

    def test_creation_of_text(self):
        create_formatted_report("Ok, everything ok!")



if __name__ == '__main__':
    unittest.main()