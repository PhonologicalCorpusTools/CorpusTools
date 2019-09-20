
from multiprocessing import Process, process, Manager, Queue, cpu_count, Value, Lock, Pool, JoinableQueue
from queue import Empty, Full

import time


def pool_filter(func, candidates, num_cores):
    pool = Pool(num_cores)
    return [c for c, keep in zip(candidates,pool.map(func,candidates)) if keep]

class Counter(object):
    def __init__(self, initval=0):
        self.val = Value('i', initval)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def value(self):
        with self.lock:
            return self.val.value

class Stopped(object):
    def __init__(self, initval=False):
        self.val = Value('i', initval)
        self.lock = Lock()

    def stop(self):
        with self.lock:
            self.val.value = True

    def stop_check(self):
        with self.lock:
            return self.val.value

class QueueAdder(Process):
    def __init__(self, iterable, queue, stopped):
        Process.__init__(self)
        self.iterable = iterable
        self.queue = queue
        self.stopped = stopped

    def run(self):
        for item in self.iterable:
            if self.stopped.stop_check():
                break
            while True:
                if self.stopped.stop_check():
                    break
                try:
                    self.queue.put(item,False)
                    break
                except Full:
                    pass
        self.queue.close()
        print('queue adder worker returning!')
        return

class FilterWorker(Process):
    def __init__(self, job_q, filtered_q, filter_function, counter, stopped):
        Process.__init__(self)
        self.job_q = job_q
        self.filtered_q = filtered_q
        self.filter_function = filter_function
        self.counter = counter
        self.stopped = stopped

    def run(self):
        results = list()
        while True:
            self.counter.increment()
            try:
                args = self.job_q.get(timeout=1)
            except Empty:
                break
            try:
                for a in args:
                    if self.filter_function(*a):
                        results.append(a)
            except Exception as e:
                self.stopped.stop()
                self.filtered_q.put(e)
                break
            self.job_q.task_done()
        if self.stopped.stop_check():
            return
        if len(results) > 0:
            self.filtered_q.put(results)


        print('filter worker returning!')
        return

def chunks(l, n):
    for i in range(0,len(l), n):
        yield l[i:i+n]


def filter_mp(iterable, filter_function, num_procs, call_back, stop_check, debug = False):
    job_queue = JoinableQueue(100)
    filtered_queue = Queue()
    stopped = Stopped()
    done = False
    while not done:
        chunk = []
        while len(chunk) < 500:
            try:
                item = next(iterable)
            except StopIteration:
                done = True
                break
            chunk.append(item)
        try:
            job_queue.put(chunk,False)
        except Full:
            break
    procs = []

    counter = Counter()
    for i in range(num_procs):
        p = FilterWorker(job_queue, filtered_queue, filter_function, counter, stopped)
        procs.append(p)
        p.start()
    val = 0
    done = False
    while not done:
        if stop_check is None:
            break
        if stop_check is not None and stop_check():
            stopped.stop()
            time.sleep(1)
            break
        chunk = []
        while len(chunk) < 500:
            try:
                item = next(iterable)
            except StopIteration:
                done = True
                break
            chunk.append(item)
        job_queue.put(chunk)

        if call_back is not None:
            value = counter.value()
            call_back(value)
    job_queue.join()
    if debug:
        print('queueadder joined!')
    return_list = list()
    error = None
    while True:
        try:
            l = filtered_queue.get(timeout=2)
        except Empty:
            break
        if isinstance(l, Exception):
            error = l
        else:
            return_list.extend(l)
    if debug:
        print('emptied result queue')
    for p in procs:
        p.join()
    if error is not None:
        raise(error)
    if debug:
        print('joined')
        print(len(return_list))
    return return_list

class ScoreWorker(Process):
    def __init__(self, job_q, scored_q, function, counter, stopped):
        Process.__init__(self)
        self.job_q = job_q
        self.scored_q = scored_q
        self.function = function
        self.counter = counter
        self.stopped = stopped

    def run(self):
        while True:
            self.counter.increment()
            try:
                args = self.job_q.get(timeout=1)
            except Empty:
                break
            results = list()
            for a in args:
                try:
                    score = self.function(*a)
                    if score is None:
                        continue
                    return_value = tuple([x for x in a] + [score])
                    results.append(return_value)
                except Exception as e:
                    self.scored_q.put(e)
                    self.stopped.stop()
                    break
            self.job_q.task_done()
            if self.stopped.stop_check():
                continue
            self.scored_q.put(results)

        return


def score_mp(iterable, function, num_procs, call_back, stop_check, debug = False, chunk_size = 500):
    job_queue = JoinableQueue(100)
    scored_queue = Queue()
    stopped = Stopped()
    done = False
    while not done:
        chunk = []
        while len(chunk) < chunk_size:
            try:
                item = next(iterable)
            except StopIteration:
                done = True
                break
            chunk.append(item)
        try:
            job_queue.put(chunk,False)
        except Full:
            break
    procs = []

    counter = Counter()
    for i in range(num_procs):
        p = ScoreWorker(job_queue, scored_queue, function, counter, stopped)
        procs.append(p)
        p.start()
    val = 0
    done = False
    while not done:
        if stop_check is None:
            break
        if stop_check is not None and stop_check():
            stopped.stop()
            time.sleep(1)
            break
        chunk = []
        while len(chunk) < chunk_size:
            try:
                item = next(iterable)
            except StopIteration:
                done = True
                break
            chunk.append(item)
        job_queue.put(chunk)

        if call_back is not None:
            value = counter.value()
            call_back(value)
    job_queue.join()
    time.sleep(2)
    if debug:
        print('queueadder joined!')
    return_list = list()
    error = None
    while True:
        try:
            l = scored_queue.get(timeout=2)
        except Empty:
            break
        if isinstance(l, Exception):
            error = l
        else:
            return_list.extend(l)
    if debug:
        print('emptied result queue')
    for p in procs:
        p.join()
    if error is not None:
        raise(error)
    if debug:
        print('joined')
        print(len(return_list))
    return return_list

