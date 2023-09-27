from collections import deque
import time
import numpy as np

class CalcFPS:
    def __init__(self, nsamples: int = 50):
        self.framerate = deque(maxlen=nsamples)

    def start_time(self):
        self.start = time.time()

    def update(self, duration: float):
        self.framerate.append(duration)

    def accumulate(self):
        if len(self.framerate) > 1:
            return int(np.average(self.framerate))
        else:
            return 0
        
    def calculate(self):
        self.update(1.0 / (time.time() - self.start))
        return self.accumulate()