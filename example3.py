import threading
import time
import subprocess
import shlex
from sys import stdout


# Only data wihtin a class are actually shared by the threads.
# Let's use a class as communicator (there could be problems if you have more than
# a single thread)
class Communicator(object):
    counter = 0
    stop = False
    arg = None
    result = None

# Here we can define what you want to do. There are other methods to do that
# but this is the one I prefer.
class ThreadedFunction(threading.Thread):

    def run(self, *args, **kwargs):
        super().run()
        command = c.arg

        # Here what you want to do...
        command = shlex.split(command)
        print(time.time()) # this is just to check that the command (sleep 5) is executed
        output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        print('\n',time.time())
        c.result = output
        if c.stop: return None # This is useful only within loops within threads

# Create a class instance
c = Communicator()
c.arg = 'time sleep 5' # Here I used the 'time' only to have some output

# Create the thread and start it
t = ThreadedFunction()
t.start() # Start the thread and do something else...

# ...for example count the seconds in the mean time..
try:
    for j in range(100):
        c.counter += 1
        stdout.write('\r{:}'.format(c.counter))
        stdout.flush()
        time.sleep(1)
        if c.result != None:
            print(c.result)
            break
except:
    c.stop = True
