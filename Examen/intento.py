import numpy as np
import time
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank() #Le nombre des processus
size = comm.Get_size() #Nombre total des processus dans le communicateur

matriz = np.empty((10, 2), dtype=np.int64)

salto = 10 // size
start = rank*salto
end=start+salto

matriz[start:end,:] = rank
lista = matriz[start:end,:]

comm.Allgather(lista, matriz)
