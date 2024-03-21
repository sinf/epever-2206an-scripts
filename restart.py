import os
import sys
import time

def restart():
    os.execve(sys.executable, [sys.executable]+sys.argv, os.environ)

def main():
    path=sys.executable
    argv=sys.argv
    env=os.environ
    print('pid:', os.getpid())
    print('path:', path)
    print('argv:', argv)
    print('env:', env)
    n=int(env.get('FORKBOMB', '10'))
    if n > 0:
        env['FORKBOMB']=str(int(n - 1))
        time.sleep(0.1)
        restart()
    print('only get here if FORKBOMB=0')

main()

