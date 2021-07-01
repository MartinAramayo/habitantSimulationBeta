import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from random import seed
import seaborn as sns 
## need to add parent directory to PYTHONPATH before importing 
import os, sys

sys.path.append(os.path.join('modules'))
import mystat as mst
import habitant as hbt
from habitant import SimulationStats
import auxPlot as aplot

def simulation_histogram(data, extra_index, names, columns):
    values, counts = np.unique(data, return_counts=True)
    counts_norm = counts/counts.sum()
    aux_array = np.asarray((counts, counts_norm)).T
    tuple_index = list(zip([extra_index]*values.size, values))
    aux_df = pd.DataFrame(aux_array, columns=columns)
    return aux_df

plt.ion()
##################################################################    
num_houses = 10000
my_mu = 2.7
ratio = 0.5

houses, people = hbt.condicion_inicial(num_houses, 
                                   ratio, 
                                   my_mu=my_mu, 
                                   house_size=None)

#############################################
Stats2 = hbt.SimulationStats(people, houses)

### get household size dataframe for plotting
household_size = tuple(len(h) for h in houses.values() if h!=[0])

# dataframe for plotzz
aux_df = pd.DataFrame(household_size, columns=['household_size'])

# plot household size
fig3, ax3 = plt.subplots()
sns.histplot(aux_df, ax=ax3)
aplot.plot_household(fig3, ax3, 'tests', "household_size.pdf")