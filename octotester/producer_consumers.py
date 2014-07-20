import datetime
import functools
import logging
import multiprocessing
import signal
import time
import threading
import traceback
import sys

from multiprocessing import Pool, Queue
from Queue import Empty as QEmpty


CLOSING_SIGNAL = 'close'
NUMBER_OF_PROCESSES = 5


TIME_BETWEEN_CHECKS = datetime.timedelta(hours=1)

# Signals that once received will trigger warm shutdown. When received during
# warm shutdowning, will perform cold shutdown.
WARM_SIGNALS = [signal.SIGTERM, signal.SIGINT]

# Receiving those signals will cause a cold shutdown, literally terminating
# process pool and exiting the master process. Use SIGKILL(9) to immediately
# terminate the master process leaving zombies behind.
COLD_SIGNALS = [signal.SIGQUIT]


class TaskExecutor(object):

    def __init__(self, get_new_tasks, process_task,
                 store_result, logging_config=None, *args , **kwargs):
        if logging_config is not None:
            logging.basicConfig(**logging_config)

        self.pool = None

        self.queue = Queue()
        self.control_queue = Queue()
        self.output_queue = Queue()
        self.finish_after_done = False

        self.shutting_down = False
        self.terminating = False
        self.process_task = process_task
        self.store_result = store_result
        self.get_new_tasks = get_new_tasks
        self._lock = threading.Lock()

    def do_task(self, queue, control_queue, output_queue):
        # Unregister signal handlers inherited from the master process.
        for signum in WARM_SIGNALS + COLD_SIGNALS:
            signal.signal(signum, signal.SIG_DFL)

        my_pid = multiprocessing.current_process().pid

        while True:
            # Check control queue for possible closing signals.
            try:
                msg = control_queue.get_nowait()
            except QEmpty:
                pass
            else:
                if msg == CLOSING_SIGNAL:
                    logging.debug(u'Received CLOSING_SIGNAL.')
                    break

            # Check regular queue for data to process with timeout so that we will
            # not starve control queue.
            try:
                msg = queue.get(timeout=10)
            except QEmpty:
                logging.debug(u'Timed out reading from queue.')
                continue

            try:
                # the job
                output = self.process_task(msg)
                output_queue.put(output)
            except Exception:
                # omg!
                logging.error("Error during task execution in process: %s" % (my_pid) +
                             traceback.format_exc())

    def _serve_tasks(self):
        """Main loop that does serve questions to the pool."""
        while True:
            tasks = self.get_new_tasks()

            for task in tasks:
                self.queue.put(task)

            try:
                output = self.output_queue.get_nowait()
            except QEmpty:
                pass
            else:
                self.store_result(output)

            if self.finish_after_done:
                break
            time.sleep(1)


    def _setup_signals(self):
        def signal_wrapper(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                return f(exit=True)
            return wrapper

        for signum in WARM_SIGNALS:
            signal.signal(signum, signal_wrapper(self.shutdown))

        for signum in COLD_SIGNALS:
            signal.signal(signum, signal_wrapper(self.terminate))

        logging.debug(u'Signals setup.')

    def shutdown(self, exit=False):
        """ Performs warm shutdown cleaning up the pool and related resources.
            If `exit` is True, stops any further execution and exits.
        """
        terminate = False
        with self._lock:
            if self.shutting_down:
                # If `exit`, then we need to terminate urgently.
                if exit and not self.terminating:
                    terminate = True
                else:
                    logging.info(u'Shutdown request during shutting down. Ignoring.')
                    return

            self.shutting_down = True

        if terminate:
            self.terminate(exit=exit)

        if self.queue is not None:
            logging.info(u'Sending %d closing signals.', NUMBER_OF_PROCESSES)
            for _ in xrange(NUMBER_OF_PROCESSES):
                self.control_queue.put(CLOSING_SIGNAL)

            logging.debug(u'Sent closing signals.')
            self.queue.close()
            self.control_queue.close()
            self.queue = None

        if self.pool is not None:
            self.pool.close()
            self.pool.join()
            self.pool = None

        if exit:
            sys.exit(0)

    def terminate(self, exit=True):
        """ Cold shutdown requested - terminate the pool and return.
            If `exit` is True, stops any further execution and exits.
        """
        with self._lock:
            if self.terminating:
                logging.info(u'Shutdown request during termination. Ignoring.')
                return

            self.shutting_down = True
            self.terminating = True

        logging.info(u'Cold shutdown requested.')
        if self.pool is not None:
            self.pool.terminate()
            self.pool = None

        if exit:
            sys.exit(0)

    def handle(self, *args, **options):
        logging.info(u'Starting %d pool processes.', NUMBER_OF_PROCESSES)

        self._setup_signals()
        try:
            self.pool = Pool(
                processes=NUMBER_OF_PROCESSES,
                initializer=self.do_task,
                initargs=(self.queue, self.control_queue, self.output_queue),
            )

            self._serve_tasks()
        finally:
            self.shutdown()
            logging.debug(u'Job done.')
