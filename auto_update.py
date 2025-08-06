import os
import time

os.system('pip install -r requirements-linux.txt')

while True:
    os.system('python ./GetNodes.py 3')
    os.system('git add .')
    os.system('git commit -m "update"')
    os.system('git push')

    time.sleep(21600)
