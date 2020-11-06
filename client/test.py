from time import time


while True:
    t = time()
    print(int(str(round(t, 1))[-1:]) < 5)