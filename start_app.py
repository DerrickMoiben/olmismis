import os
import subprocess
import sys

def start_django():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.Popen([sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'])

if __name__ == '__main__':
    start_django()
