from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank() #Le nombre des processus
size = comm.Get_size() #Nombre total des processus dans le communicateur

def vanessa():
    if rank==0:
        jeton=1
        comm.send(jeton,dest=1)
        print("Hola, soy ", rank, "y Jeton inicial= ",jeton)
        jeton=comm.recv(source=size-1)
        print("Hola, soy ", rank, "y Jeton final= ",jeton)
    elif (rank!=0 and rank!=size-1):
        jeton=comm.recv(source=rank-1)
        jeton=jeton+1
        comm.send(jeton,dest=rank+1)
        print("Hola, soy ", rank ," y Jeton= ",jeton)
    else:
        jeton=comm.recv(source=rank-1)
        jeton=jeton+1
        comm.send(jeton,dest=0)
        print("Hola, soy ", rank, " ultimo"," y Jeton= ",jeton)

def gustavo():
    if rank==0:
        print("Hi, I am ", rank)
        data=1
        req=comm.isend(data,dest=1)
        req.wait()
        end_process=comm.irecv(source=size-1)
        data=end_process.wait()
        print(f"Hi, I am {rank} and I received {data}")
    
    elif rank!=size-1:
        print("Hi, I am ", rank)
        req=comm.irecv(source=rank-1)
        data=req.wait()
        data=data+1
        req=comm.isend(data,dest=rank+1)
    else:
        print("Hi, I am ", rank)
        req=comm.irecv(source=rank-1)
        data=req.wait()
        data=data+1
        req=comm.isend(data,dest=0)

gustavo()