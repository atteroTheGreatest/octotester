
from producer_consumers import TaskExecutor

from Queue import Empty as QEmpty



class TestMaster(object):
    def __init__(self, changes_queue):
        self.changes_queue = changes_queue
        self.mapper = ChangeToTestMapper()
        self.executor = TaskExecutor(get_new_tasks=self.get_test_names_to_run,
                                     process_task=TestRunner(),
                                     store_result=self.store_result)
    def get_test_names_to_run(self):
        names = []
        try:
            while True:
                change = self.changes_queue.get(block=False)
                test_name = self.mapper.map_to_test(change)
                names.append(test_name)
        except QEmpty:
            pass
        if names:
            print "New names!"
            print set(names)
        return set(names)

    def store_result(self, output):
        print "OMG, result!"
        print output


    def run(self):
        self.executor.handle()


class ChangeToTestMapper(object):

    def validate_change(self, change):
        return True

    def map_to_test(self, change):
        # magic, magic!
        return "tests/tests.py"


class TestRunner(object):

    def __init__(self):
        print "Test runner starts!"

    def show_report(self, test_output):
        return "Here is a report: %s" % test_output

    def run(self, test):
        return "OK"

    def tear_up_environment(self, *args, **kwargs):
        pass

    def tear_down_environment(self, *args, **kwargs):
        pass

    def __call__(self, test):
        self.tear_up_environment()
        test_output = self.run(test)
        self.tear_down_environment()
        report = self.show_report(test_output)
        return report

class DjangoTestRunner(TestRunner):
    pass