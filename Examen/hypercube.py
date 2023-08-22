from mpi4py import MPI
import time
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
n_proc = comm.Get_size()
status = MPI.Status()

comm.Barrier()
deb = time.time()

vector = np.zeros(100, dtype=int)
if rank == 0:
    vector = np.ones(100, dtype=int)

# Broadcast in a hypercube
dimension = int(np.log2(n_proc))

for step in range(dimension):
    #Determina el proceso actual 
    tmp_rank = rank >> step  #Desplazamiento a la derecha en los bits de rank en la cantidad step (Se descarta el bit menos signif (bit a la derecha))
    
    print("tmp_rank ", rank, tmp_rank, tmp_rank >> step)
    # Determina si el proceso actual es la fuente (enviar data) o destino (recibir data)

    if tmp_rank >> step == 0: #Fuente 
        neighbor = my_rank ^ (1 << step)  # ^ es el operador XOR (desplaza 1 bit a la izquierda)
        comm.Send(vector, dest=neighbor)
    else:  # Destino 
        comm.Recv(vector, source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)

comm.Barrier()
end = time.time()

print(f"I am process {rank}, last element of my vector after broadcast is {vector[-1]}")

if rank == 0:
    print(f"operation time: {end - deb} [s]")

MPI.Finalize()


