import time ### timing
start_time = time.time()
### modules
import matplotlib.pyplot as plt
from random import randint
from random import seed
from copy import copy
from pprint import pprint
from matplotlib import cm
import seaborn as sns 

## need to add parent directory to PYTHONPATH before importing 
import os, sys
#################### open and set experiment
import yaml

def experiment_from_file(experiment_yaml):
    with open(experiment_yaml) as file:
        experiment = yaml.full_load(file)
    return experiment
   
dirname, child_dirs, files = next(os.walk(os.getcwd()))

fig, ax = plt.subplots()

num_plots = 200
for a_file in files:
    
    if 'yaml' in a_file:
        experiment = experiment_from_file(a_file)
    else:
        continue
    
    num_houses = experiment['initial_condition']['num_houses']
    execution_time = experiment['execution_time_sec']
    
    aux_args = {'color': 'salmon'}
    ax.scatter(num_houses, execution_time, **aux_args)
    ax.set_xlabel('# Casas al iniciar')
    ax.set_ylabel('Tiempo de ejecucion')

fig.tight_layout()
fig.savefig('timeVsSize.pdf')