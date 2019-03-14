import time
import subprocess
import shlex
from sys import stdout


command = 'time sleep 5' # Here I used the 'time' only to have some output

def x(command):
    cmd = shlex.split(command)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p

# Start the subprocess and do something else...
p = x(command)
# ...for example count the seconds in the mean time..

try: # This take care of killing the subprocess if problems occur
    for j in range(100):
        stdout.write('\r{:}'.format(j))
        stdout.flush()
        time.sleep(1)
        if p.poll() != None:
            print(p.communicate())
            break
except:
    p.terminate() # or p.kill()
