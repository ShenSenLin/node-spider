import os
import time


while True:
    os.system('python ./GetNodes.py')
    os.system('git add .')
    os.system('git commit -m "update"')
    os.system('git push')

    time.sleep(43200)