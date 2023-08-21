from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

data = []

if rank == 0:
    data = [[2, 1], [3, 4, 5]]
elif rank == 1:
    data = [[1, 2, 3, 4, 5], [6, 7, 8]]
elif rank == 2:
    data = [[1, 2, 3, 4, 5], [9, 10]]

all_data = comm.allgather(data)

print(all_data)