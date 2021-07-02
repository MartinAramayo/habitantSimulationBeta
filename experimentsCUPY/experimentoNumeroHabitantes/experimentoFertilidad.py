import numpy as np
import time ### timing
start_time = time.time()
### modules
import matplotlib.pyplot as plt
from matplotlib import cm

## need to add parent directory to PYTHONPATH before importing 
import os, sys
#################### open and set experiment
import yaml

def experiment_from_file(experiment_yaml):
    with open(experiment_yaml) as file:
        experiment = yaml.full_load(file)
    return experiment
   
data = []
dirname, child_dirs, files = next(os.walk(os.getcwd()))
for a_file in files:
    
    if 'yaml' in a_file:
        experiment = experiment_from_file(a_file)
    else:
        continue
    
    num_houses = experiment['initial_condition']['num_houses']
    execution_time = experiment['execution_time_sec']
    data.append([num_houses, execution_time])

data = np.asarray(data)
with open('../../experimentGPU.npy', 'wb') as f:
    np.save(f, data)

fig, ax = plt.subplots()
aux_args = {'color': 'salmon'}
ax.scatter(data[:,0], data[:,1], **aux_args)
ax.set_xlabel('# Casas al iniciar')
ax.set_ylabel('Tiempo de ejecucion')

fig.tight_layout()
fig.savefig('timeVsSize.pdf')