import termcolor
import unittest2

from collections import defaultdict
from Queue import Empty as QEmpty

from producer_consumers import TaskExecutor


def create_formatted_report(report_text):
    if "Error" in report_text or "Failure" in report_text:
        text = text = termcolor.colored(report_text, 'red')
    else:
        text = termcolor.colored(report_text, 'green')
    return text


class TestMaster(object):
    def __init__(self, changes_queue, root_directory):
        self.changes_queue = changes_queue

        self.executor = TaskExecutor(get_new_tasks=self.get_test_names_to_run,
                                     process_task=TestRunner(root_directory),
                                     store_result=self.display_result)
    def get_test_names_to_run(self):
        names = []
        try:
            while True:
                change = self.changes_queue.get(block=False)

                names.append(change)
        except QEmpty:
            pass
        if names:
            print "New names!"
            print set(names)
        return set(names)

    def display_result(self, output):
        text_to_display = create_formatted_report(output)
        print text_to_display

    def run(self):
        self.executor.handle()


class ChangeToTestMapper(object):
    def __init__(self, directory):
        self.directory = directory
        self.test_file_to_suite = defaultdict(dict)
        tests = unittest2.defaultTestLoader.discover(directory)
        for test in tests:
            for sub_test in test:

                string_info = str(sub_test)
                print string_info
                path_parts = string_info.split("tests=")[1].split(" ")[0][2:].split(".")
                file_name = "/".join(path_parts[:-1])
                suite_name = path_parts[-1]
                self.test_file_to_suite[file_name][suite_name] = sub_test
                print self.test_file_to_suite[file_name][suite_name]

    def validate_change(self, change):
        return True

    def strip_changed_filename(self, filename):
        if not self.directory or len(self.directory) < 2:
            directory_first = "octotester"
        else:
            directory_first = self.directory.split("/")[0]
        directory_first = "octotester"
        print "filename", filename
        path_parts = []
        ready = False
        for path_part in filename.split("/"):
            if path_part == directory_first:
                ready = True
            if ready:
                path_parts.append(path_part)
        print "Striped filename", "/".join(path_parts)
        return "/".join(path_parts[1:]).split(".")[0]

    def map_to_test(self, change):
        # magic, magic!
        striped = self.strip_changed_filename(change)
        print striped
        return self.test_file_to_suite[striped]


class TestRunner(object):

    def __init__(self, root_directory):
        self.mapper = ChangeToTestMapper(root_directory)
        self.runner = unittest2.TextTestRunner()

    def show_report(self, test_output):
        return "Here is a report: %s" % test_output

    def run(self, test):
        return "OK"

    def tear_up_environment(self, *args, **kwargs):
        pass

    def tear_down_environment(self, *args, **kwargs):
        pass

    def __call__(self, test_filepath):
        print "Start new test!"
        tests = self.mapper.map_to_test(test_filepath).values()
        test_output = ""
        print tests
        for test in tests:
            self.tear_up_environment()
            test_output += str(self.runner.run(test))
            self.tear_down_environment()
        report = self.show_report(test_output)
        return report

class DjangoTestRunner(TestRunner):
    pass
