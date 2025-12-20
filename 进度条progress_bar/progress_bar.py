from time import sleep
from rich.progress import track

for step in track(range(10)):
    sleep(1)
    print(step)




