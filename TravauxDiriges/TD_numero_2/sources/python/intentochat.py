import numpy as np
from mpi4py import MPI
import random

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
root = 0

def original():
    local_array = [rank] * random.randint(2, 5)
    print("rank: {}, local_array: {}".format(rank, local_array))

    sendbuf = np.array(local_array)

    # Collect local array sizes using the high-level mpi4py gather
    sendcounts = np.array(comm.gather(len(sendbuf), root))

    if rank == root:
        print("sendcounts: {}, total: {}".format(sendcounts, sum(sendcounts)))
        recvbuf = np.empty(sum(sendcounts), dtype=int)
    else:
        recvbuf = None

    comm.Gatherv(sendbuf=sendbuf, recvbuf=(recvbuf, sendcounts), root=root)
    if rank == root:
        print("Gathered array: {}".format(recvbuf))

def matrix():
    local_array = [rank] * np.ones([random.randint(2, 5), random.randint(2, 5)])
    print("rank: {}, local_array: {}".format(rank, local_array))

    sendbuf = np.array(local_array) #Creo que esta linea sobre
    print("-----",local_array.shape)
    
    # Collect local array sizes using the high-level mpi4py gather
    sendcounts = np.array(comm.gather(local_array.shape, root))

    if rank == root:
        print("sendcounts: {}, total: {}".format(sendcounts, sum(sendcounts)))
        recvbuf = np.empty(sum(sendcounts), dtype=int)
    else:
        recvbuf = None
    '''
    comm.Gatherv(sendbuf=sendbuf, recvbuf=(recvbuf, sendcounts), root=root)
    if rank == root:
        print("Gathered array: {}".format(recvbuf))
    '''

def chatgpt():
    # Data to send from each process
    send_data = np.array([rank] * (rank + 1), dtype=int)
    print(send_data,sum(range(size)))
    print("------")


    # Gather the data on the root process
    if rank == 0:
        recv_data = np.empty(sum(range(size)), dtype=int)  # Receive buffer
        recvcounts = [i + 1 for i in range(size)]  # Number of elements from each process
        displs = [sum(recvcounts[:i]) for i in range(size)]  # Displacements
        print(recv_data,recvcounts,displs)
    else:
        recv_data = None
        recvcounts = None
        displs = None
    '''
    # Perform MPI_Gatherv
    comm.Gatherv(send_data, [recv_data, recvcounts, displs, MPI.INT], root=0)

    # Print the gathered data on the root process
    if rank == 0:
        print("Gathered data:", recv_data)

    # Finalize MPI
    '''
    MPI.Finalize()

matrix()