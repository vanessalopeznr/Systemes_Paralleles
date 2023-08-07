# Run: mpirun -np 2 python3 mpi-python.py 

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
    jeton=0
    if rank == 0:
        print('Hola, soy el proceso 0')
        datos = np.arange(100, dtype=np.float64)
        comm.Send(datos, dest=1, tag=13)
        #data = np.array([1], dtype='i')
        #comm.Send([data, MPI.INT], dest=1)
        print('Proceso 0: Enviando datos...')
        time.sleep(2)
        jeton=jeton+100
        print('Proceso 0: Continuando después del envío...')
        print('Proceso 0: Jeton= ',jeton)
    elif rank == 1:
        print('Hola, soy el proceso 1')
        print('Proceso 1: Esperando recibir datos...')
        time.sleep(10)
        datos = np.empty(100, dtype=np.float64)
        comm.Recv(datos, source=0, tag=13)
        #data = np.empty(1, dtype='i')
        #comm.Recv([data, MPI.INT], source=0)
        print('Proceso 1: Datos recibidos:', datos)

    '''
    Con la lista "datos" se comporta de manera bloqueante (El proceso 0 no puede seguir hasta 
    recibir la confirmacion de recepcion del proceso 1) ya que en la comunicacion hay un buffer y 
    una "lista de espera" de la red, cada comando tiene un buffer (en este caso la "datos") y 
    cuando este es muy grande para la lista de espera, esta se llena, el buffer queda con el resto 
    de informacion y bloquea el proceso.
    Por ende, en las lineas comentadas, "data" no bloquea la comunicacion ya que su talla es muy 
    pequeña.

    send --> Mpi determina bloqueante o no
    isend --> Siempre es no bloqueante
    Send --> Siempre bloqueante (Dependiendo de la talla del mensaje)
    '''

def Reduce():

    nbSamples=80

    x = np.random.random_sample((nbSamples,))
    approx_pi_loc=np.add.reduce(x,0)   #Suma los puntos de x con add y con reduce se escoge el eje 0 (por filas)
    approx_pi_glob = np.zeros(1, dtype=np.double)
    comm.Allreduce(approx_pi_loc, approx_pi_glob, MPI.SUM) #Sumar

    print(f"Pi vaut environ {approx_pi_glob}")

def scatter_data():

    if rank == 0:
        data = [(i+1)**2 for i in range(size)]
    else:
        data = None
    data = comm.scatter(data, root=0)

    print("i am", rank, " and my data is: ", data)

def gather_data():

    data = (rank+1)**2
    data = comm.gather(data, root=0)

    if rank == 0:
        print("i am", rank, " and my data is: ", data)

def Broadcast_array():

    if rank == 0:
        data = np.arange(100, dtype='i')
    else:
        data = np.empty(100, dtype='i')

    comm.Bcast(data, root=0)
    print("i am", rank, " and my data is: ", data)

def scatter_array():

    sendbuf = None

    if rank == 0:
        sendbuf = np.empty([1,size*2], dtype='i')
        sendbuf[:,:] = range(size) # Esta linea de codigo rellena en columnas [range(size) es (0,4)]
        print(sendbuf[:,:])


    recvbuf = np.empty(2, dtype='i')
    comm.Scatter(sendbuf, recvbuf, root=0)
    print("i am", rank, " and my data is: ", recvbuf)

def gather_array():

    sendbuf = np.zeros(20, dtype='i') + rank+1 #Todos los valores de send toman el numero de rank
    recvbuf = None

    if rank == 0:
        recvbuf = np.empty([size, 20], dtype='i')

    comm.Gather(sendbuf, recvbuf, root=0)
    print("i am", rank, " and my data is: ", recvbuf) #Proceso 0 recibe matrix (filas size, columnas 20)

    # Verifica si el valor recibido es igual al rank, sino da error
    if rank == 0:
        for i in range(size):
            assert np.allclose(recvbuf[i,:], i+1)

def gather_array_var():

    sendbuf = np.zeros((5,5), dtype='i') + rank #Todos los valores de send toman el numero de rank
    recvbuf = None

    salto=25./size
    start=rank*salto
    end=start+salto

    convergence = np.empty((5,5),dtype=np.double)

    for i in range(start,end):
        for j in range(5):
            convergence[i,j] = i+j
    
    sendbuf = convergence[:]

    if rank == 0:
        recvbuf = np.empty(25, dtype='i')

    comm.Gather(sendbuf, recvbuf, root=0)
    print("i am", rank, " and my data is: ", recvbuf) #Proceso 0 recibe matrix (filas size, columnas 20)
    

gather_array()
