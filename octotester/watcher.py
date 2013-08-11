
import pyinotify


class EventHandler(pyinotify.ProcessEvent):

    def __init__(self, changes_queue, *args, **kwargs):
        self.changes_queue = changes_queue
        super(EventHandler, self).__init__(*args, **kwargs)

    def process_IN_MODIFY(self, event):
        print "Modifying:", event.pathname
        self.changes_queue.put(event.pathname)

    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname
        self.changes_queue.put(event.pathname)


def watch_for_changes_on_disk(changes_queue, directory='/tmp'):
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY

    handler = EventHandler(changes_queue)
    notifier = pyinotify.Notifier(wm, handler)

    try:
        print "CREATE WATCHER"
        wdd = wm.add_watch(directory, mask, rec=True)

        notifier.loop()
    finally:
        wm.rm_watch(wdd.values())
        print "REMOVE WATCHER"