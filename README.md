# Systèmes parallèles et distribués

Ubuntu version: [Ubuntu](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-11-with-gui-support#1-overview) 

Working with Visual Studio Code on Ubuntu: [Vscode in Ubuntu](https://ubuntu.com/tutorials/working-with-visual-studio-code-on-ubuntu-on-wsl2#1-overview)

Configuration [Git in vscode](https://code.visualstudio.com/docs/sourcecontrol/github)

## Commands for upload the repository in GitHub from vscode

```
git add *
git commit -m "Upload README"
git push
```
## Install libraries

Install OPEN MPI librarie (mpirun is used to run MPI program and mpicc is used to compile MPI programs in C (Make executable) and mpic++ compile programs in C++)

```
sudo apt install openmpi-bin
sudo apt install libopenmpi-dev
```

Install MPI for Python (Il faut avoir libopenmpi-dev)
```
sudo apt install python3-pip
python3 -m pip install mpi4py
```

### Pour parallelize les bucles en C++:

 Il faut mettre sur les bucles `#pragma omp parallel for collapse(3)` for parallelize le 3 bucles dans ce cas et sur le command pour executer le code, il faut prèciser le nombre de coeurs.

`make TestProductMatrix.exe && OMP_NUM_THREADS=8 ./TestProductMatrix.exe 1024`

Si le command ne dit pas le nombre de threads, l'ordinateur prend tous les coeurs disponibles. (in my case 6)

ou c'est possible aussi préciser tous les instructions sur le ligne au code `#pragma omp parallel for num_threads(6) collapse(3)`
 
### Pour parallelize en Python:

Il faut toujours mettre:
	
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank() #Le nombre des processus
    size = comm.Get_size() #Nombre total des processus dans le communicateur


Pour executer le code, il faut utiliser la commande: 
    
    mpirun -np <nombre de processus> python3 <nombre fichier>
    

[PASTELITO MPI PYTHON](https://github.com/vanessalopeznr/Systemes_Paralleles/blob/main/Programs/mpi-python.py)

- The lower-case variants `comm.bcast`, `comm.scatter`, `comm.gather`, `comm.allgather` and `comm.alltoall` can communicate general Python objects. The vector variants (which can communicate different amounts of data to each process) `comm.Scatterv`, `comm.Gatherv`, `comm.Allgatherv`, `comm.Alltoallv` and `comm.Alltoallw` are also supported, they can only communicate objects exposing memory buffers.
- `comm.Send(data,dest=<nombre rank>)` and `comm.Recv(source=<nombre rank>)` used to send and receive the data. **Blocking communications**.
- the `comm.isend` and `comm.irecv` return a Request instance, uniquely identifying the started operation. **Non-blocking communications**. (Ej. If you want to receive data sometimes without blocking communication).
- `comm.bcast(data, root=0)` used to broadcast the data to all the processes and root is the rank of the process that is going to send the data.
- When you want to receive the data and you don't know the rank of the process that is going to send the data, you can use `comm.Irecv(source=MPI.ANY_SOURCE)`

Con una lista de datos grande se comporta de manera bloqueante (El proceso 0 no puede seguir hasta recibir la confirmacion de recepcion del proceso 1) ya que en la comunicacion hay un buffer y una "lista de espera" de la red, cada comando tiene un buffer y cuando este es muy grande para la lista de espera, esta se llena, el buffer queda con el resto de informacion y bloquea el proceso.
Por ende, un dato o lista de datos pequeño no bloquea la comunicacion ya que su talla es muy pequeña.

send --> Mpi determina bloqueante o no
isend --> Siempre es no bloqueante
Send --> Siempre bloqueante (Dependiendo de la talla del mensaje)

Non-blocking communications: `comm.isend` and `comm.irecv`

```
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        data = {'a': 7, 'b': 3.14}
        req = comm.isend(data, dest=1, tag=11)
        req.wait()
    elif rank == 1:
        req = comm.irecv(source=0, tag=11)
        data = req.wait()
    
```

Blocking: `comm.Send` and `comm.Recv`

```
    from mpi4py import MPI
    import numpy

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    # passing MPI datatypes explicitly
    if rank == 0:
        data = numpy.arange(1000, dtype='i')
        comm.Send([data, MPI.INT], dest=1, tag=77)
    elif rank == 1:
        data = numpy.empty(1000, dtype='i')
        comm.Recv([data, MPI.INT], source=0, tag=77)
    
```	
Blocking and non-blocking : `comm.send` and `comm.recv`

    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        data = {'a': 7, 'b': 3.14}
        comm.send(data, dest=1, tag=11)
    elif rank == 1:
        data = comm.recv(source=0, tag=11)

## Collective communication

**MPI_Reduce :** Operar envios de todos los procesos

<img width="388" alt="image" src="https://github.com/vanessalopeznr/Voiture-autonome-ELEGOO/assets/123451768/cc983abc-357c-43b2-acb9-843b44c71a6a">

    approx_pi_loc=4.*sum/nbSamples
    approx_pi_glob = np.zeros(1, dtype=np.double)
    comm.Allreduce(approx_pi_loc, approx_pi_glob, MPI.SUM) #Sumar

<img width="368" alt="image" src="https://github.com/vanessalopeznr/Voiture-autonome-ELEGOO/assets/123451768/e971ae27-c714-4300-a66e-68480376bb97">

**MPI_Allreduce:** Operar envios de todos los procesos y enviar el resultado a todos los procesos

<img width="387" alt="image" src="https://github.com/vanessalopeznr/Voiture-autonome-ELEGOO/assets/123451768/7d4d1cad-ac21-4f6d-bc14-e275006f4873">


**MPI_Scan:** Operar envios de los procesos progresivamente y envia

<img width="380" alt="image" src="https://github.com/vanessalopeznr/Voiture-autonome-ELEGOO/assets/123451768/ba96c761-643b-43e4-83b7-ae93f3cb4db5">

**Broadcast:** Enviar datos a todos los procesos

<img width="370" alt="image" src="https://github.com/vanessalopeznr/Voiture-autonome-ELEGOO/assets/123451768/10710845-3c0d-4bad-a366-f84bea57c777">

Broadcasting a Python dictionary:

    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        data = {'key1' : [7, 2.72, 2+3j],
                'key2' : ( 'abc', 'xyz')}
    else:
        data = None
    data = comm.bcast(data, root=0)

Broadcasting a NumPy array:

    from mpi4py import MPI
    import numpy as np

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        data = np.arange(100, dtype='i')
    else:
        data = np.empty(100, dtype='i')
    comm.Bcast(data, root=0)
    for i in range(100):
        assert data[i] == i

**MPI_Scatter :** Distribuir datos a todos los procesos

<img width="488" alt="image" src="https://github.com/vanessalopeznr/Voiture-autonome-ELEGOO/assets/123451768/3f5bf419-4339-40a5-8975-30b87bf68ac6">

Scattering Python objects:

    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    if rank == 0:
        data = [(i+1)**2 for i in range(size)]
    else:
        data = None
    data = comm.scatter(data, root=0)
    assert data == (rank+1)**2

Scattering NumPy arrays:

    from mpi4py import MPI
    import numpy as np

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    sendbuf = None
    if rank == 0:
        sendbuf = np.empty([size, 100], dtype='i')
        sendbuf.T[:,:] = range(size)
    recvbuf = np.empty(100, dtype='i')
    comm.Scatter(sendbuf, recvbuf, root=0)
    assert np.allclose(recvbuf, rank)

**MPI_Gather :** Recopilar datos de todos los procesos en un solo proceso

<img width="433" alt="image" src="https://github.com/vanessalopeznr/Voiture-autonome-ELEGOO/assets/123451768/6ea81d12-d0ad-4974-864f-a3dc88bb1599">

Gathering Python objects:

    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    data = (rank+1)**2
    data = comm.gather(data, root=0)
    if rank == 0:
        for i in range(size):
            assert data[i] == (i+1)**2
    else:
        assert data is None

Gathering NumPy arrays:

    from mpi4py import MPI
    import numpy as np

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    sendbuf = np.zeros(100, dtype='i') + rank
    recvbuf = None
    if rank == 0:
        recvbuf = np.empty([size, 100], dtype='i')
    comm.Gather(sendbuf, recvbuf, root=0)

    #Verifica si el valor recibido es igual al rank, sino da error

    if rank == 0:
        for i in range(size):
            assert np.allclose(recvbuf[i,:], i)

**MPI_Allgather :** Recopilar datos de todos los procesos en todos los procesos

<img width="468" alt="image" src="https://github.com/vanessalopeznr/Voiture-autonome-ELEGOO/assets/123451768/355b6593-2295-4ae4-855d-22cc9cab2f24">

Creacion de elementos:

    np.ones(4) #Lista de unos de 4 cifras
    np.ones([2,3]) #Matriz de 2 filas x 3 columnas