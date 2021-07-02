import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
aux_args = {'color': 'salmon', 'label':'CPU'}
with open('experimentCPU.npy', 'rb') as f:
    data = np.load(f)
ax.scatter(data[:,0], data[:,1], **aux_args)

aux_args = {'color': 'lime', 'label':'GPU'}
with open('experimentGPU.npy', 'rb') as f:
    data = np.load(f)
ax.scatter(data[:,0], data[:,1], **aux_args)

ax.set_xlabel('# Casas al iniciar')
ax.set_ylabel('Tiempo de ejecucion(s)')

ax.legend()

ax.set_yscale('log')
ax.set_xscale('log')

fig.tight_layout()
fig.savefig('timeVsSize.pdf')