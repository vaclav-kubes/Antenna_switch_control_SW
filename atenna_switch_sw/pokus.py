import threading
import queue
import time

def do1():
    print("start")
    q.put(True)
    time.sleep(5)
    q.get()
    q.task_done()
    
def do2():
    q.put(True)
    print("hotovo")

q = queue.Queue(1)

t1 = threading.Thread(target = do1, daemon = True)
t1.start()

t2 = threading.Thread(target = do2, daemon = True)
t2.start()