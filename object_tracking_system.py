from scripts.object_tracking import Track
from Config import N_GPU
import torch.multiprocessing as mp

process = []
for i in range(N_GPU):
    p = mp.Process(target=Track, args=(i,))
    p.start()
    process.append(p)
    
for p in process:
    p.join()