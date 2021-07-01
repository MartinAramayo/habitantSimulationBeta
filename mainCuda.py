import time ### timing
start_time = time.time()
### modules
import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from random import randint
from random import seed
from copy import copy
from pprint import pprint
from matplotlib import cm
import seaborn as sns 

## need to add parent directory to PYTHONPATH before importing 
import os, sys

sys.path.append(os.path.join('modules'))
# import mystat as mst
import habitant as hbt
from habitant import SimulationStats
import auxPlot as aplot

#################### seed
seed(202)
from numpy.random import MT19937
from numpy.random import RandomState, SeedSequence
rs = RandomState(MT19937(SeedSequence(123456789)))
# Later, you want to restart the stream
rs = RandomState(MT19937(SeedSequence(987654322)))
#################### docstring
"""
the logic implies a maximum of two kids per year
Parameters: 
    n_iteraciones : iteraciones de la simulacion
    num_people : numero de personas iniciales
    p_emancipate : probabilidad de emanciparse
    p_partner : probabilidad de conseguir pareja
    p_child : probabilidad de tener un bebe
    p_child : probabilidad de una muerte prematura
"""
#################### open and set experiment

from shutil import copyfile   
import yaml

# select yaml file, load to dictionary
experiment_yaml = sys.argv[1]
experiment = hbt.experiment_from_file(experiment_yaml)
experiment_dir = os.path.splitext(experiment_yaml)[0]

# define variables from dictionary
n_iteraciones = experiment['n_iteraciones']
# num_people = experiment['num_people']
p_emancipate = experiment['p_emancipate']
p_partner = experiment['p_partner']
p_child = experiment['p_child']
p_premature_death = experiment['p_premature_death']
initial_condition = experiment['initial_condition']

# create directories if they don't exist yet
# experiment_dir = 'experiments/' + os.path.splitext(experiment_yaml)[0]
try: 
    os.mkdir(experiment_dir)
    os.mkdir(experiment_dir + "/logs")
    os.mkdir(experiment_dir + "/plots")
except FileExistsError:
    pass

"""
 ███████╗████████╗ █████╗ ██████╗ ████████╗
 ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝
 ███████╗   ██║   ███████║██████╔╝   ██║   
 ╚════██║   ██║   ██╔══██║██╔══██╗   ██║   
 ███████║   ██║   ██║  ██║██║  ██║   ██║   
 ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
"""

## create a house and people system
houses, people = hbt.condicion_inicial(**initial_condition)

## logs 
num_data_df = pd.DataFrame()

step = 0

## number data stats
aux_args = {
    "other": SimulationStats(people, houses).number_get_stats(),
    "ignore_index": True
}      
num_data_df = num_data_df.append(**aux_args)
    
for step in range(1, n_iteraciones):
       
    # print("-------------------------- Step: ", step)
    lista_nh = copy(list(people.keys()))
    for nh in lista_nh: ## use a copy of the current population
        
        ## age population and kill old habitants
        habitant = people[nh]
        habitant.age_step() # aging
        if not habitant.is_alive:
            nc = habitant.nc
            hbt.kill(houses=houses, people=people, nh=nh, nc=nc) # deaths
    
    if people == {}: break
    
    lista_nh = copy(list(people.keys()))
    ###################################### child birth GOOOD
    possible_parents = cp.asarray(
        tuple(nh for nh in lista_nh 
         if (people[nh].middle_life 
             and people[nh].emancipated
             and people[nh].partner
             and hbt.is_fertile_couple(people, nh))
         ), 
        dtype=int)
    
    a_kargs = {'size': possible_parents.size, 'p': (1-p_child, p_child)}
    num_parents = int(cp.sum(cp.random.choice((False, True), **a_kargs)))
    
    a_kargs = {'size':num_parents, 'replace':False}
    possible_parents = cp.random.choice(possible_parents, **a_kargs) 
    # toma algunos padres AL AZAR para que tengan hijos
    for nh in possible_parents:
        hbt.simulating_birth(houses, people, people[int(nh)].nc)
    ###################################### single people GOOD
    single_people = cp.asarray(
        tuple(nh for nh in lista_nh 
        if (not people[nh].partner 
            and people[nh].middle_life)
        ), 
        dtype=int)
    
    # get how many new couples are going to be formed
    a_kargs = {'size': single_people.size, 'p': (1-p_partner, p_partner)}
    new_couples = int(cp.sum(cp.random.choice((False, True), **a_kargs)))//2
    
    a_kargs = {'size':2*new_couples, 'replace':False}
    single_people = cp.random.choice(single_people, **a_kargs)
    # toma algunas parejas AL AZAR !!!
    for nh1, nh2 in single_people.reshape((single_people.size//2, 2)):
        hbt.create_couple(people, int(nh1), int(nh2))
    ################################## Moving out
    movable = cp.asarray(
        tuple(nh for nh in lista_nh 
         if (not people[nh].emancipated
             and people[nh].middle_life)
         ), 
        dtype=int)
    
    a_kargs = {'size': movable.size, 'p': (1-p_emancipate, p_emancipate)}
    num_movable = int(cp.sum(cp.random.choice((False, True), **a_kargs)))
    
    a_kargs = {'size':num_movable, 'replace':False}
    movable = cp.random.choice(movable, **a_kargs)
    
    empty_houses = cp.asarray(
        tuple(nh for nh, house in houses.items() if house == [0]), 
        dtype=int)
    cp.random.shuffle(empty_houses)

    for nh, nc in zip(movable, empty_houses): ## use a copy of the current population
        habitant = people[int(nh)]
        habitant.moving_out(houses, people, int(nc))     
    ############################################### Getting metrics
    ## number data stats
    aux_args = {
        "other": SimulationStats(people, houses).number_get_stats(),
        "ignore_index": True
    }      
    num_data_df = num_data_df.append(**aux_args)
        
"""
 ██████╗ ██╗      ██████╗ ████████╗
 ██╔══██╗██║     ██╔═══██╗╚══██╔══╝
 ██████╔╝██║     ██║   ██║   ██║   
 ██╔═══╝ ██║     ██║   ██║   ██║   
 ██║     ███████╗╚██████╔╝   ██║   
 ╚═╝     ╚══════╝ ╚═════╝    ╚═╝   
"""

num_iterations = num_data_df.index[-1] + 1

## plot occupation
aplot.plot_occupation(num_data_df, experiment_dir)

# number data stats
non_stats = ['num_houses', 'num_non_empty_houses', 'num_empty_houses']
rename_dict = {'num_births': 'Nacimientos',
               'num_couples': 'Parejas',
               'num_emancipated': 'Emancipados',
               'num_non_empty_houses': 'Viviendas deshabitadas',
               'num_gender_1': 'Genero 1',
               'num_gender_2': 'Genero 2',
               'num_habitants': 'Habitantes',
               'num_houses': 'Viviendas',
               'num_middle_life': 'Adultos',
               'num_non_empty_houses': 'Viviendas vacias'}

aux_args = {"figsize":(4, 12), "subplots":True}
axs = num_data_df.drop(
    non_stats, axis=1).rename(
        columns=rename_dict
        ).plot.area(**aux_args)
aplot.num_plot(axs, experiment_dir)

"""
 ███████╗ █████╗ ██╗   ██╗███████╗
 ██╔════╝██╔══██╗██║   ██║██╔════╝
 ███████╗███████║██║   ██║█████╗  
 ╚════██║██╔══██║╚██╗ ██╔╝██╔══╝  
 ███████║██║  ██║ ╚████╔╝ ███████╗
 ╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝
"""

num_data_df.to_pickle(experiment_dir + "/logs/num_data_df.pkl")

###################################################### LOGS

import time

## logs
experiment['execution_time_sec'] = time.time() - start_time
experiment['num_iterations_real'] = int(num_iterations)
experiment['MIDDLE_LIFE_START'] = hbt.MIDDLE_LIFE_START
experiment['MIDDLE_LIFE_END'] = hbt.MIDDLE_LIFE_END
experiment['LIFE_EXPECTANCY'] = hbt.LIFE_EXPECTANCY
experiment['INFANCY'] = hbt.INFANCY
experiment['HOUSE_CAP'] = hbt.HOUSE_CAP
experiment['execution_time'] = time.ctime()

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PreservedScalarString as pss
from ruamel.yaml.scalarstring import FoldedScalarString as fss

yaml2 = YAML()

## comment hack
experiment['comment'] = pss(experiment['comment'])

with open(experiment_dir + "/plots/log.yaml", 'w') as file:
    yaml2.dump(experiment, file)
with open(experiment_dir + "/logs/log.yaml", 'w') as file:
    yaml2.dump(experiment, file)
with open(experiment_yaml, 'w') as file:
    yaml2.dump(experiment, file)