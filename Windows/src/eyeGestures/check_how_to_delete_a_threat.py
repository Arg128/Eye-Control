from threading import Thread, Lock
from time import sleep

mylocking = Lock()
counter = 0
def increase(by):
    with mylocking:
        global counter
        local_counter = counter
        local_counter += by
        sleep(0.1)
        counter = local_counter
        print(f'counter={counter}')

t1 = Thread(target=increase, args=(10,))
t2 = Thread(target=increase, args=(20,))

# start the threads
t1.start()          #JUST START XDE
t2.start()

# wait for the threads to complete
t1.join()
t2.join()           #JOIN --> WAIT EVEN FINISHEM

print(f'The final counter is {counter}')
argi = 0
COUNTER = 10
def something(arg, i):
    with mylocking:
        global argi
        local_arg = argi
        local_arg += arg
        argi = local_arg
        print("Im in lock 3: ", i)

def middle_worker(i):
    athread = Thread(target=something, args=(COUNTER, i))
    myThreats.append(athread)
    athread.start()
    print("Im in lock 2: ", i)

def i_want_to_add_something(i):
    with mylocking:
        print("Im in lock 1: ", i)
        middle_worker(i)


myThreats = []
i = 0
while (i <= 10):
    i_want_to_add_something(i)
    i += 1

print("///////////////////////////////////////////////////////////")
print(argi)

for task in myThreats:
    print(task)
    print(task.is_alive())   
    if not task.is_alive():
        print("DELETING TASK N°: ", task)
        task = None

for task in myThreats:
    if task is None:
        continue
    print(task)
    print(task.is_alive())
    if not task.is_alive():
        print("DELETING TASK N°: ", task)
        task = None
myThreats.clear()

athread2 = Thread(target=something, args=(COUNTER, i))

print(athread2)
athread2 = None
print(athread2)
print((myThreats))




























#                                       LOCKING AND LOVE IN TO TOT RO THOR RANSMOMSWARE XDE


"""                when you put the with LOCK statement; this cancels every self function calling to this prosses until unlock to the endlest part """