# import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from random import randint
import copy
from pprint import pprint
from matplotlib import cm
import yaml

# funciones de apoyo
## need to add parent directory to PYTHONPATH before importing 
import os, sys
sys.path.append(os.path.join('..', 'chadFieldwork', 'modules'))

import mystat as mst
import random

"""
Reglas: 
    - Ninguna casa tiene numero 0
    - Si partner == 0 no tiene pareja (un False)
    - Ningun habitante tiene 
    nh(numero de habitante) == 0
    - gender es True/False (binarios) 
    e identicos respecto a su dinamica
"""

# SIMULATION PARAMETERS
MIDDLE_LIFE_START = 20
MIDDLE_LIFE_END = 50
LIFE_EXPECTANCY = 85
INFANCY = 14
HOUSE_CAP = 10

## asume que el diccionario tiene keys enteros
def new_key_number(dictionary):
    """Devuelve el ultimo key del diccionario + 1
    si no hay keys, devuelve un 1

    Args:
        dictionary (dictionary): Diccionario con keys enteros

    Returns:
        int: nuevo key para un diccionario de keys enteros
    """
    ## OJO ESTO SOLO ES CIERTO SI SE PRESERVA EL ORDEN
    # return max(dictionary.keys()) + 1 if dictionary else 1 
    # need to create a list
    return [*dictionary.keys()][-1] + 1 if dictionary else 1 # for older python versions
    # return next(reversed(dictionary.keys())) + 1 if dictionary else 1

def recien_nacido(nh, nc, gender):
    
    recien_nacido = { 
        "nh": nh, 
        "nc": nc, 
        "age": 0, 
        "gender": gender, 
        "emancipated": False, 
        "partner": 0
        }
    return recien_nacido

class Habitant:
  
    def __init__(self,
                 nh,
                 nc,
                 age,
                 gender,
                 emancipated,
                 partner,
                 is_fertile_couple=False,
                 ): 
        self.nh = nh
        self.nc = nc
        self.age = age
        self.gender = gender
        self.emancipated = emancipated
        self.partner = partner
        
        self.middle_life = (self.age > MIDDLE_LIFE_START 
                            and self.age < MIDDLE_LIFE_END)
        
        self.is_child = self.age < INFANCY
        
        self.is_alive = (self.age >= 0 
                         and self.age < LIFE_EXPECTANCY)
        
        self.is_fertile_couple = is_fertile_couple
        
    def __repr__(self):
        list_args = [
            f'nh={self.nh}',
            f'nc={self.nc}',
            f'age={self.age}',
            f'gender={self.gender}',
            f'emancipated={self.emancipated}',
            f'partner={self.partner}'
        ]
        str_args = ', '.join(list_args)
        return f'Habitant({str_args})'
    
    def __str__(self):
        list_args = [
            f'nh={self.nh:05d}',
            f'nc={self.nc:05d}',
            f'age={self.age:05d}',
            f'gender={str(self.gender):5s}',
            f'emancipated={str(self.emancipated):5s}',
            f'partner={self.partner:05d}'
        ]
        str_args = ', '.join(list_args)
        return f'Habitant({str_args})'
    
    def age_step(self): # updates age, set middle_age
        
        self.age += 1
        
        self.middle_life = (self.age > MIDDLE_LIFE_START 
                            and self.age < MIDDLE_LIFE_END)
        
        self.is_alive = (self.age >= 0 
                         and self.age < LIFE_EXPECTANCY)
        
        self.is_child = self.age < INFANCY
    
    def moving_out(self, houses, people, nc):
    
        nh, old_nc = self.nh, self.nc
        nh_partner = self.partner
        
        emancipated_partner = (
            nh_partner
            and people[nh_partner].emancipated 
        )
        
        new_nc = (people[nh_partner].nc 
                  if emancipated_partner else nc)
            
        if house_has_vacant(houses, new_nc):
            self.nc = new_nc # change nc
            self.emancipated = True
            add_nh_house(houses, nh, new_nc) # add nh to house
            delete_nh_house(houses, nh, old_nc) # delete nh from old house

def create_couple(people, nh_1, nh_2):
    people[nh_1].partner = nh_2
    people[nh_2].partner = nh_1
    
def house_has_vacant(houses, nc):
    return (len(houses[nc]) < HOUSE_CAP)

# return boolean
def is_fertile_couple(people, nh): # gender exclusive or
    habitante = people[nh]
    if habitante.partner:
        pareja_habitante = people[habitante.partner]
        return habitante.gender ^ pareja_habitante.gender
    else:
        return False
    
def tener_hijo(nc, nh, gender):
    nuevo_recien_nacido = recien_nacido(nh, nc, gender)
    hijoHabitante = Habitant(**nuevo_recien_nacido)
    return hijoHabitante

def add_nh_house(houses, nh, nc): # send boolean if succed
    if houses[nc] == [0]:
        houses[nc] = [nh]
    else: 
        houses[nc].append(nh)
    
def delete_nh_house(houses, nh, nc):
    index = (houses[nc]).index(nh)
    del houses[nc][index]
    if houses[nc] == []:
        houses[nc] = [0]
        
def kill(houses, people, nh, nc):
    
    # update fallen partner attributes
    if people[nh].partner:
        people[people[nh].partner].partner = 0
    
    delete_nh_house(houses, nh, nc)
    del people[nh]

def simulating_birth(houses, people, nc):
    if house_has_vacant(houses, nc):
        nh_hijo = new_key_number(people)
        hijoHabitante = tener_hijo(nc=nc,
                                nh=nh_hijo, 
                                gender=bool(randint(0,1))
                                )
        people.update({nh_hijo: hijoHabitante})
    
        add_nh_house(houses, 
                     nc=hijoHabitante.nc, 
                     nh=hijoHabitante.nh)

############################################## construct initial condition

def create_empty_world(num_houses):
    houses = {nc: [0] for nc in range(1, num_houses+1)}
    return houses, dict()

def ratio_sample_house_inhabited(houses, ratio):
    # Returns the keys of all habitated houses
    # ratio habtiadas/ totales
    b = [*houses.keys()]
    kargs = {'a':b, 'size':int(len(b) * ratio), 'replace':False}
    return np.random.choice(**kargs)
    
def fill_random_from_house_size(houses, people, nc_sample, house_sizes):
    for nc, size in zip(nc_sample, house_sizes):
        while house_size(houses, nc) < size:
            insert_people(houses, people, nc)
      
def age_house(houses, people, nc):
    # everyone in the house gets older
    for nh in houses[nc]:
        habitant = people[nh]
        habitant.age_step()
        if not habitant.is_alive:
            hbt.kill(houses=houses, people=people, nh=nh, nc=nc) # deaths
      
def insert_people(houses, people, nc):
    size = house_size(houses, nc)
    if size == 0:
        nh = new_key_number(people)
        gender = bool(randint(0,1))
        habitante = Habitant(**nuevo_adulto(nh, nc, 0, gender))
        add_habitant(habitante, houses, people)
    elif size == 1:
        habitante = people[houses[nc][0]]
        create_partner(habitante, houses, people)
    else: # elif size >= 2:
        age_house(houses, people, nc)
        simulating_birth(houses, people, nc)    

def create_partner(habitant, houses, people):
    nh, nc, gender = habitant.nh, habitant.nc, habitant.gender
    if house_has_vacant(houses, nc):
        nh_p = new_key_number(people)
        habitant.partner = nh_p
        partner = Habitant(**nuevo_adulto(nh_p, nc, nh, not gender))
        add_habitant(partner, houses, people)
        
def add_habitant(habitante, houses, people):
    nc, nh = habitante.nc, habitante.nh
    add_nh_house(houses, nc=nc, nh=nh)
    people.update({nh: habitante})
    
def nuevo_adulto(nh_1, nc, nh_2, gender):
    p1 = {"nh": nh_1, 
          "nc": nc, 
          "age": randint(MIDDLE_LIFE_START, MIDDLE_LIFE_END), 
          "gender": gender, 
          "emancipated": True, 
          "partner": nh_2}
    return p1

def nuevos_padres(nh_1, nc, gender):
    p1 = {"nh": nh_1, 
          "nc": nc, 
          "age": randint(MIDDLE_LIFE_START, MIDDLE_LIFE_END), 
          "gender": gender, 
          "is_fertile_couple": True,
          "emancipated": True, 
          "partner": nh_1 + 1}
    p1 = {"nh": nh_1 + 1, 
          "nc": nc, 
          "age": randint(MIDDLE_LIFE_START, MIDDLE_LIFE_END), 
          "gender": not gender, 
          "is_fertile_couple": True,
          "emancipated": True, 
          "partner": nh_1}
    return p1, p2
       
def insert_new_couple(houses, people, nh_1, nc):
    gender = bool(randint(0,1))
    
    p1, p2 = nuevos_padres(nh_1, nc, gender)
    persona1, persona2 = Habitant(**p1), Habitant(**p2)
    add_nh_house(houses, nh_1, nc)
    add_nh_house(houses, nh_1 + 1, nc)
    
    people.update({nh_1:persona1, nh_1+1:persona2})
    
def new_inhabited_home(houses, people):
    nc, nh_1 = new_key_number(houses), new_key_number(people)
    insert_new_couple(houses, people, nh_1, nc)
    
def get_empty_house(houses):
    empty_house = [nh for nh, house in houses.items() if house == [0]]
    return empty_house
    
def house_size(houses, nc):
    house = houses[nc]
    if house == [0]:
        return 0
    else:
        return len(house)
    
def condicion_inicial(num_houses, ratio, house_size=None, my_mu=None):
    ## creo num_houses numero de casas, con un ratio (habtiadas/ totales)
    ## hay dos opciones, o todas las casa con el mismo house size
    ## o en una poisson de parametro my_mu
    houses, people = create_empty_world(num_houses=num_houses)

    # me quedo con las viviendas habitadas, respetando el ratio
    nc_sample = ratio_sample_house_inhabited(houses, ratio)

    if house_size is not None:
        house_sizes = np.repeat(house_size, nc_sample.size)
    if my_mu is not None:
        # genero los tamaños de household
        args1, args2 = {'a': 1, 'seed': 150}, {'mu': my_mu, 'size': nc_sample.size}
        house_sizes = mst.truncated_poisson(**args1).rvs(**args2)

    # lleno con los householdsize
    fill_random_from_house_size(houses, people, nc_sample, house_sizes)
    return houses, people
    
############################################### STATS
    
class SimulationStats:
    
    def __init__(self, people, houses): 
        self.nh = [p.nh for p in people.values()]
        self.nc = [p.nc for p in people.values()]
        self.age = [p.age for p in people.values()]
        
        self.gender = [p.gender for p in people.values()] # gender
        self.emancipated = [p.emancipated for p in people.values()] #emancipated
        self.middle_life = [p.middle_life for p in people.values()] # middle life
        self.childs = [p.is_child for p in people.values()] # middle life
        self.partner = [p.partner for p in people.values()] # partner
        
        self.num_habitants = len(people)
        
        self.num_gender_1 = sum(self.gender)
        self.num_gender_2 = self.num_habitants - self.num_gender_1
        self.num_emancipated = sum(self.emancipated)
        self.num_middle_life = sum(self.middle_life)
        self.num_couples = sum(bool(partner) for partner in self.partner)
        self.num_childs = sum(bool(is_child) for is_child in self.childs)
        self.num_births = sum(1 for p in people.values() if p.age == 0)
        
        self.num_houses = len(houses) 
        self.num_empty_houses = sum(1 for h in houses.values() if h==[0])
        self.num_non_empty_houses = self.num_houses - self.num_empty_houses
        
    def number_get_stats(self):
        
        output = {
            "num_habitants": self.num_habitants,
            "num_gender_1": self.num_gender_1,
            "num_gender_2": self.num_gender_2,
            "num_emancipated": self.num_emancipated,
            "num_middle_life": self.num_middle_life,
            "num_couples": self.num_couples,
            "num_births": self.num_births,
            "num_houses": self.num_houses,
            "num_empty_houses": self.num_empty_houses,
            "num_non_empty_houses": self.num_non_empty_houses
        }        
        return output
        
class SimulationStatsNUMPY:
    
    def __init__(self, people_table, houses, empty_houses): 
        self.age            = people_table[:, 2]
        self.gender         = people_table[:, 3]        
        self.emancipated    = people_table[:, 4] #emancipated
        self.partner        = people_table[:, 5] # partner
        self.middle_life    = people_table[:, 6] # middle life
        self.childs         = people_table[:, 7] # child
        self.fertile_couple = people_table[:, 9] # child
        
        self.num_habitants = len(people_table)
        
        self.num_gender_1 = sum(self.gender)
        self.num_gender_2 = self.num_habitants - self.num_gender_1
        self.num_emancipated = sum(self.emancipated)
        self.num_middle_life = sum(self.middle_life)
        self.num_couples = sum(self.partner > 0)
        self.num_childs = sum(self.childs)
        self.num_births = sum(self.childs == 0)
        
        self.num_houses = len(houses) 
        self.num_empty_houses = len(empty_houses)
        self.num_non_empty_houses = self.num_houses - self.num_empty_houses
        
    def number_get_stats(self):
        
        output = {
            "num_habitants": self.num_habitants,
            "num_gender_1": self.num_gender_1,
            "num_gender_2": self.num_gender_2,
            "num_emancipated": self.num_emancipated,
            "num_middle_life": self.num_middle_life,
            "num_couples": self.num_couples,
            "num_births": self.num_births,
            "num_houses": self.num_houses,
            "num_empty_houses": self.num_empty_houses,
            "num_non_empty_houses": self.num_non_empty_houses
        }        
        return output

# class SimulationStatsCUPY:
    
#     def __init__(self, people_table, houses, empty_houses): 
#         self.age            = people_table[:, 2]
#         self.gender         = people_table[:, 3]        
#         self.emancipated    = people_table[:, 4] #emancipated
#         self.partner        = people_table[:, 5] # partner
#         self.middle_life    = people_table[:, 6] # middle life
#         self.childs         = people_table[:, 7] # child
#         self.fertile_couple = people_table[:, 9] # child
        
#         self.num_habitants = len(people_table)
        
#         self.num_gender_1 = int(cp.sum(self.gender))
#         self.num_gender_2 = self.num_habitants - self.num_gender_1
#         self.num_emancipated = int(cp.sum(self.emancipated))
#         self.num_middle_life = int(cp.sum(self.middle_life))
#         self.num_couples = int(cp.sum(self.partner > 0))
#         self.num_childs = int(cp.sum(self.childs))
#         self.num_births = int(cp.sum(self.age == 0))
        
#         self.num_houses = len(houses) 
#         self.num_empty_houses = len(empty_houses)
#         self.num_non_empty_houses = self.num_houses - self.num_empty_houses
        
#     def number_get_stats(self):
        
#         output = {
#             "num_habitants": self.num_habitants,
#             "num_gender_1": self.num_gender_1,
#             "num_gender_2": self.num_gender_2,
#             "num_emancipated": self.num_emancipated,
#             "num_middle_life": self.num_middle_life,
#             "num_couples": self.num_couples,
#             "num_births": self.num_births,
#             "num_houses": self.num_houses,
#             "num_empty_houses": self.num_empty_houses,
#             "num_non_empty_houses": self.num_non_empty_houses
#         }        
#         return output

############################################### Experiments files

def file_selector():
    print("Elige un numero para realizar un experimento:")
    files = []
    i = 0
    for x in os.listdir('experiments'):
        if x.endswith(".yaml"): # Prints only yaml experiment files
            print(f"{i}) {x}")
            files.append(x)
            i += 1
    try: 
        eleccion = int(input(">> "))
    except ValueError: 
        print("No es un valor valido: ValueError")
        print("Mejor suerte la próxima :)")
        exit()
        
    try: 
        experiment_yaml = files[eleccion]
        print("Elegiste:\n", experiment_yaml)
    except IndexError:
        print("No es un valor valido: IndexError")
        print("Mejor suerte la próxima :)")
        exit()

    return experiment_from_file(experiment_yaml)

def experiment_from_file(experiment_yaml):
    with open(experiment_yaml) as file:
        experiment = yaml.full_load(file)
    return experiment