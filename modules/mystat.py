import numpy as np 
from numpy import exp

# # distribuciones
from scipy.stats import rv_discrete
from scipy.special import factorial

# distribuciones
from scipy.stats import poisson
from scipy.stats import rv_discrete

# producing poisson predictions
class truncated_poisson(rv_discrete):
    "Truncated Poisson distribution"
    def _pmf(self, k, mu):
        return (mu**k / factorial(k)) * ( exp(-mu) / (1 - exp(-mu)) )