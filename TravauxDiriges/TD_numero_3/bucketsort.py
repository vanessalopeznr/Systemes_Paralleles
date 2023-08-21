import numpy as np
import time
from mpi4py import MPI
import sys
from itertools import chain

comm = MPI.COMM_WORLD
rank = comm.Get_rank() #Le nombre des processus
size = comm.Get_size() #Nombre total des processus dans le communicateur

if len(sys.argv) > 1:
    N = int(sys.argv[1])

def non_paral():
    values = np.random.randint(-32768, 32768, size=N,dtype=np.int64)
    debut = time.time()
    values.sort()
    fin=time.time()
    print("Me demore: ", fin-debut)

def paral_maestro_0():
    debut = time.time()
    maximo=200
    minimo=-200
    #Division de datos dependiendo del numero de procesos
    if N%size > rank:
        salto = N//size + 1

    else:
        salto = N//size

    recvbuf = np.empty(salto,dtype=np.int64)
    values=None

    #Creacion de datos por rank 0
    if rank==0:
        values = np.random.randint(minimo, maximo, size=N,dtype=np.int64)

    #Envio de datos a cada proceso [reparticion dinamica (no repart equitativa) por eso scatterv]
    comm.Scatterv(values, recvbuf, root=0)

    #Organizacion de datos
    recvbuf.sort()

    #Calculo de medianas
    mediana=np.empty(size, dtype=np.int64)
    for i in range(size):
        mediana[i] = int(salto/size)*i

    #Envio de medianas al proceso 0
    medcounts = np.array(comm.gather(recvbuf[mediana], 0))

    #Organizacion de medianas y envio de limites a buckets
    index_limites=np.empty(size, dtype=np.int64)
    limites=np.empty(2, dtype=np.int64)

    if rank == 0:
        array_medianas = np.ravel(medcounts)
        array_medianas.sort()
        for i in range(size):
            index_limites[i] = int(array_medianas.size/size)*i

        for lim in range(1,index_limites.size):
            limites=array_medianas[index_limites[lim:lim+2]]
            comm.send(limites, dest=lim)
        limites=[minimo,array_medianas[index_limites][1]]
        print(rank, limites)
    
    if rank != 0:
        limites = comm.recv(source=0)
        if rank==size-1:
            limites=np.append(limites,maximo)
        print(rank, limites)
    
    fin=time.time()
    print("Me demore: ", fin-debut)

def paral():
    debut = time.time()
    maximo=200
    minimo=-200
    #Division de datos dependiendo del numero de procesos
    if N%size > rank:
        salto = N//size + 1

    else:
        salto = N//size

    #Creacion de datos de talla Salto
    values = np.random.randint(minimo, maximo, size=salto,dtype=np.int64)

    deb=time.time()
    #Organizacion de datos
    values.sort()

    #Calculo de pivotes (Se ignora la buena distribucion del pivote en las listas que salto no es divisible por size )
    pivots=np.empty(size-1, dtype=np.int64)
    for i in range(1,size):
        pivots[i-1] = int(salto/size)*i 

    #Envio de pivotes a todos los procesos
    all_pivots = np.empty(size*(size-1),dtype=np.int64)
    comm.Allgather(values[pivots], all_pivots)
    
    #Organizacion de pivotes
    all_pivots.sort()

    #Calculo de limites
    index_limites=np.empty(size-1, dtype=np.int64)
    for i in range(1,size):
            index_limites[i-1] = int(all_pivots.size/size)*i
    
    limites=all_pivots[index_limites]

    #Organizacion de datos de este proceso en todos los limites 
    bucket=[]

    bucket.append(values[values <= limites[0]].tolist())

    for p in range(1,size-1):
        bucket.append(values[np.logical_and(values <= limites[p],values > limites[p-1])].tolist())

    bucket.append(values[values > limites[size-2]].tolist())
    
    #Envio de listas organizadas a bucket correspondiente (Este paso penaliza mucho el tiempo)
    my_values = None
    for p in range(size):
        if p == rank :
            my_values = comm.gather(bucket[p], root=p)
        else:
            comm.gather(bucket[p], root=p)
    
    #Maneras de convertir una lista de listas en una lista
    #val_ready = [item for sublist in my_values for item in sublist]
    #val_ready = list(chain.from_iterable(my_values))

    val_ready = sum(my_values, [])
    val_ready.sort()

    fin=time.time()
    print("Me demore: ", fin-debut)

paral()