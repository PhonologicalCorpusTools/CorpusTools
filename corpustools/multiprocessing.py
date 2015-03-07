
from multiprocessing import Process, Manager, Queue, cpu_count, Value, Lock, Pool
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

class CallBackWorker(Process):
    def __init__(self, call_back, counter, max_value, stopped):
        Process.__init__(self)
        self.call_back = call_back
        self.counter = counter
        self.max_value = max_value
        self.stopped = stopped

    def run(self):
        pass


def call_back_worker(call_back, counter, max_value, stopped):
    call_back(0, max_value)
    while True:
        if stop_check is not None and stop_check():
            break
        time.sleep(0.01)
        value = counter.value()
        if value > max_value - 5:
            break
        call_back(value)

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

def queue_adder(iterable,queue, stopped):
    while len(iterable) > 0:
        if stopped.stop_check():
            break
        item = iterable.pop(0)
        while True:
            if stopped.stop_check():
                break
            try:
                queue.put(item,False)
                break
            except Full:
                pass
    print('queue adder worker returning!')
    return

def filter_worker(job_q,return_list, filter_function, counter, stopped):
    while True:
        if stopped.stop_check():
            break
        counter.increment()
        try:
            args = job_q.get(timeout=1)
        except Empty:
            break
        if filter_function(*args):
            return_list.append(args)
    print('filter worker returning!')
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
            for a in args:
                if self.filter_function(*a):
                    results.append(a)

        if self.stopped.stop_check():
            return
        if len(results) > 0:
            self.filtered_q.put(results)
        print('filter worker returning!')
        return

def chunks(l, n):
    for i in range(0,len(l), n):
        yield l[i:i+n]


def filter_mp(iterable, filter_function, num_procs, call_back, stop_check):
    job_queue = Queue(100)
    filtered_queue = Queue()
    stopped = Stopped()
    #job_p = Process(target=queue_adder,
    #                args = (iterable,job_queue, stopped))
    #job_p = QueueAdder(iterable, job_queue, stopped)
    #job_p.start()
    while True:
        chunk = []
        while len(chunk) < 500:
            try:
                item = next(iterable)
            except StopIteration:
                break
            chunk.append(item)
        try:
            job_queue.put(chunk,False)
        except Full:
            break
    procs = []

    counter = Counter()
    #call_p = CallBackWorker(call_back, counter, max_value, stopped)
    #call_p.start()
    for i in range(num_procs):
        #p = Process(
        #        target=filter_worker,
        #        args=(job_queue,
        #              return_list, filter_function, counter, stopped))
        p = FilterWorker(job_queue, filtered_queue, filter_function, counter, stopped)
        procs.append(p)
        p.start()
    val = 0
    while True:
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
                break
            chunk.append(item)
        job_queue.put(chunk)

        #time.sleep(0.1)
        if call_back is not None:
            value = counter.value()
            call_back(value)
    #job_p.join()
    print('queueadder joined!')
    #call_p.join()
    return_list = list()
    while True:
        try:
            l = filtered_queue.get(timeout=2)
        except Empty:
            break
        return_list.extend(l)
    print('emptied result queue')
    for p in procs:
        p.join()
    print('joined')
    print(len(return_list))
    return return_list
