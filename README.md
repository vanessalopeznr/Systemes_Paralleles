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

comm.send(data,dest=<nombre rank>) and comm.recv(source=<nombre rank>) used to send and receive the data.
Note how comm.Send and comm.Recv used to send and receive the numpy array have upper case S and R.
comm.bcast(data, root=0) used to broadcast the data to all the processes and root is the rank of the process that is going to send the data.
