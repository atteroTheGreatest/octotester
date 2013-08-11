
import unittest
from octotester.testers import TestMaster
from multiprocessing import Queue


def get_new_tasks():
	print "New tasks are coming!"
	return [1, 2, 3]

def process_task(task):
	print "Task %s execution" % task
	return "OK"

def store_result(output):
	print "OMG, result!"
	print output

class TestTestMaster(unittest.TestCase):

    def setUp(self):
    	pass

    def test_master(self):
        changes_queue = Queue()
        changes_queue.put("sky!")
        changes_queue.put("sweets!")
        changes_queue.put("sweets!")
        master = TestMaster(changes_queue)
        master.run()


if __name__ == '__main__':
    unittest.main()