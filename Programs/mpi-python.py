from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank() #Le nombre des processus
size = comm.Get_size() #Nombre total des processus dans le communicateur
'''
if rank == 0:
    numData = 10  
    comm.send(numData, dest=1)

    data = np.array([1,2,3,4,5,6,7,8,9,10], dtype='int') # allocate space and create the array
    comm.Send(data, dest=1)

elif rank == 1:

    numData = comm.recv(source=0)
    print('Number of data to receive: ',numData)

    data = np.empty(numData, dtype='int')  # allocate space to receive the array, dtype='int' is also used for   
    comm.Recv(data, source=0)

    print('data received: ',data)
'''
if rank == 0:
    data = {'key1' : [1,2, 3],
            'key2' : ( 'abc', 'xyz')}
else:
    data = None

data = comm.bcast(data, root=1) #root: processus qui envoie les donnees
print('Rank: ',rank,', data: ' ,data)