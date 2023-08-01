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