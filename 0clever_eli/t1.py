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
            sleep(1)
            if self.queue.empty():
                # 判断放到get前面，这样可以，否则队列最后一个取完后就空了，直接break，走不到print
                break

            item = self.queue.get()
            print(item, '...')
            self.queue.task_done()
            """
            如果把self.queue.task_done()  注释去掉，就会顺利执行完主程序。
            这就是“Queue.task_done()函数向任务已经完成的队列发送一个信号”这句话的意义，能够让join()函数能判断出队列还剩多少，是否清空了。
            """

        return


myque = queue.Queue()
tasks = [Mythread(myque) for x in range(2)]  # 2个线程
# print(tasks)
for x in range(10):
    myque.put(x)  # 快速生产

for x in tasks:
    t = Mythread(myque)  # 把同一个队列传入2个线程
    t.start()

myque.join()

print("---finish---")
