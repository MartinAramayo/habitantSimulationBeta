import os, sys
## need to add parent directory to PYTHONPATH before importing 

sys.path.append(os.path.join('modules'))
from habitant import Habitant

# para test        
entrada = { 
    "nh": 1, 
    "nc": 1, 
    "age": 84, 
    "gender": False, 
    "emancipated": True, 
    "partner": 21
    }
fernando = Habitant(**entrada)