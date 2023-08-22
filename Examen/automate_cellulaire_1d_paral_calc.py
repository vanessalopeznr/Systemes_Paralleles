import numpy as np
import time
import matplotlib.pyplot as plt
import sys
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank() #Le nombre des processus
size = comm.Get_size() #Nombre total des processus dans le communicateur
#Para borrar resultados rm resultat_*

#nombre_cas   : int = 256
nombre_cas   : int = 256
nb_cellules  : int = 360  # Cellules fantomes
nb_iterations: int = 360

def save_as_md(cells, num_config, symbols='⬜⬛'):
    res = np.empty(shape=cells.shape, dtype='<U')
    res[cells==0] = symbols[0]
    res[cells==1] = symbols[1]
    np.savetxt(f'resultat_{num_config:03d}.md', res, fmt='%s', delimiter='', header=f'Config #{num_config}', encoding='utf-8')

if rank == 0:
    
    deb=time.time()

    task=0
    for i in range(1,size):
        print("envio a ", rank)
        comm.ssend(task,dest=i)
        task += 1

    cells = np.zeros((nb_iterations, nb_cellules+2), dtype=np.int16)
    stat = MPI.Status()
    while task < nombre_cas:
        comm.Recv(cells,status=stat)
        req=comm.isend(task, stat.Get_source())
        save_as_md(cells, stat.Get_tag())
        req.wait(None)
        task += 1
        if task==250:
            print("toy llegando")

    task = -1

    for k in range(1,size):
        comm.Recv(cells,status=stat)
        req=comm.isend(task, stat.Get_source())
        save_as_md(cells, stat.Get_tag())
        req.wait(None)
    
    fin = time.time()
    print("rank ", rank, f"Temps d'affichage des resultats : {fin-deb} secondes\n")


if rank != 0:

    deb=time.time()
    task = 0
    stat = MPI.Status()
    while task >= 0:
        task=comm.recv(source=0, status=stat)
        if task >=0:
            cells = np.zeros((nb_iterations, nb_cellules+2), dtype=np.int16) #Matriz 360*362
            cells[0, (nb_cellules+2)//2] = 1 #La mitad de la matriz cells es 1
            for iter in range(1, nb_iterations):
                vals = np.left_shift(1, 4*cells[iter-1, 0:-2]
                                    + 2*cells[iter-1, 1:-1]
                                    + cells[iter-1, 2:])
                cells[iter, 1:-1] = np.logical_and(np.bitwise_and(vals, task), 1)
            
            #Debe ser un send bloqueante, ya que si envio y el rank 0 ya me esta asignando otra tarea, se enloquece
            comm.Send(cells, 0, task)


    fin = time.time()
    print("rank ", rank, f"Temps calcul des generations de cellules : {fin-deb} secondes\n") 

