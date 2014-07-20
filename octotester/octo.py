import multiprocessing
import sys

from testers import TestMaster
from watcher import watch_for_changes_on_disk


class Octo(object):
    def run(self):
        # create queue for watcher and test master
        changes_queue = multiprocessing.Queue()


        watcher = multiprocessing.Process(target=watch_for_changes_on_disk,
                                          args=(changes_queue, self.directory,))

        watcher.start()

        # will run test when changes are visible
        master = TestMaster(changes_queue, self.directory)
        master.run()

        # why joining here?
        watcher.join()

    def __init__(self, directory):
        self.directory = directory



if __name__ == "__main__":
    directory = sys.argv[1]
    octotester = Octo(directory=directory)
    octotester.run()
