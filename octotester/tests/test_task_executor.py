import unittest

from octotester.producer_consumers import TaskExecutor


def get_new_tasks():
    return [1, 2, 3]


def process_task(task):
    print "Task %s execution" % task
    return "OK"


def store_result(output):
    print "OMG, result!"
    print output


class TaskExecutorTest(unittest.TestCase):
    """In current version it's more than demonstration that test"""
    def setUp(self):
    	pass

    def test_creating_test(self):
        executor = TaskExecutor(get_new_tasks=get_new_tasks,
                                process_task=process_task,
                                store_result=store_result)
        executor.handle()
        print "Is it all?"


if __name__ == '__main__':
    unittest.main()
