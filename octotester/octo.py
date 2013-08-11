from testers import TestMaster
import multiprocessing
from watcher import watch_for_changes_on_disk


class Octo(object):
    def run(self):
        changes_queue = multiprocessing.Queue()
        master = TestMaster(changes_queue, self.directory)

        watcher = multiprocessing.Process(target=watch_for_changes_on_disk, args=(changes_queue, self.directory,))

        watcher.start()
        master.run()

        watcher.join()

    def __init__(self, directory):
        self.directory = directory

    

if __name__ == "__main__":
    directory = raw_input("What to watch, sir? ")
    octotester = Octo(directory=directory)
    octotester.run()