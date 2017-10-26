import threading
import time
exit_flag = 0


class myThread(threading.Thread):
    def __init__(self, threadid, name, counter):
        threading.Thread.__init__(self)
        self.threadid = threadid
        self.name = name
        self.counter = counter
   
    def run(self):
        print('Starting ' + self.name)
        print_time(self.name, self.counter, 5)
        print('Exiting ' + self.name)

def print_time(threadName, counter, delay):
    while counter:
        if exit_flag:
            threadName.exit()
        time.sleep(delay)
        print(threadName, str(time.ctime(time.time())))
        counter -= 1

th1 = myThread(1, 'thread1', 10)
th2 = myThread(2, 'thread2', 20)

th1.start()
th2.start()

print('Exiting main thread')