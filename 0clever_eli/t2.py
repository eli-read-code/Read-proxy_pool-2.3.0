import threading
import queue
from time import sleep


# 之所以为什么要用线程，因为线程可以start后继续执行后面的主线程，可以put数据，如果不是线程直接在get阻塞。
class Mythread(threading.Thread):
    def __init__(self, que):
        threading.Thread.__init__(self)
        self.queue = que

    def run(self):
        while True:
            item = self.queue.get()
            self.queue.task_done()
            """
             #这里要放到判断前，否则取最后最后一个的时候已经为空，直接break，task_done执行不了，join()判断队列一直没结束
            """
            if item == None:
                break
            print(item, '...')

        return


myque = queue.Queue()
tasks = [Mythread(myque) for x in range(2)]  # 2个线程
# print(tasks)

for x in tasks:
    t = Mythread(myque)  # 把同一个队列传入2个线程
    t.start()

for x in range(10): # 慢速生产
    sleep(2)
    myque.put(x)

for x in tasks: # 快速消费
    myque.put(None)  # 结束标志

myque.join()

print("---finish---")
