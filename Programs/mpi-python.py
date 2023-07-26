from mpi4py import MPI
import numpy as np
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank() #Le nombre des processus
size = comm.Get_size() #Nombre total des processus dans le communicateur

#Send/Recv
def sendRecv():
    if rank == 0:
        data = 100
        comm.send(data, dest=1)
    elif rank == 1:
        data = comm.recv(source=0)
        print('Rank: ',rank,', data: ' ,data)

def sendRecvArray():
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

def broadcast():
    if rank == 0:
        data = 100
    else:
        data = None

    data = comm.bcast(data, root=0) #root: processus qui envoie les donnees
    print('Rank: ',rank,', data: ' ,data)

def nonblock_comm():
    if rank == 0:
        print('Hola, soy el proceso 0')
        data = {'message': 'Hello, World!', 'sender': rank}
        req = comm.isend(data, dest=1)  # Non-blocking send to rank 1
        print('Proceso 0: Enviando datos...')
        time.sleep(2)
        print('Proceso 0: Continuando después del envío...')
        
    elif rank == 1:
        print('Hola, soy el proceso 1')
        req = comm.irecv(source=0)  # Non-blocking receive from rank 0
        print('Proceso 1: Esperando recibir datos...')
        data = req.wait()  # Wait for the communication to complete and retrieve the data
        print('Proceso 1: Datos recibidos:', data)

def block_comm():
    if rank == 0:
        print('Hola, soy el proceso 0')
        data = {'message': 'Hello, World!', 'sender': rank}
        req = comm.send(data, dest=1)  # Blocking send to rank 1
        print('Proceso 0: Enviando datos...')
        time.sleep(2)
        print('Proceso 0: Continuando después del envío...')

    elif rank == 1:
        print('Hola, soy el proceso 1')
        print('Proceso 1: Esperando recibir datos...')
        req = comm.recv(source=0)  # Blocking receive from rank 0
        print('Proceso 1: Datos recibidos:', req)

block_comm()
