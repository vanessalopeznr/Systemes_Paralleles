import numpy as np
import time
import matplotlib.pyplot as plt
import sys
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank() #Le nombre des processus
size = comm.Get_size() #Nombre total des processus dans le communicateur
#Para borrar resultados rm resultat_*

nombre_cas   : int = 256
nb_cellules  : int = 360  # Cellules fantomes
nb_iterations: int = 360

def save_as_md(cells, num_config, symbols='⬜⬛'):
    res = np.empty(shape=cells.shape, dtype='<U')
    res[cells==0] = symbols[0]
    res[cells==1] = symbols[1]
    np.savetxt(f'resultat_{num_config:03d}.md', res, fmt='%s', delimiter='', header=f'Config #{num_config}', encoding='utf-8')

def save_as_png(cells):
    fig = plt.figure(figsize=(nb_iterations/10., nb_cellules/10.))
    ax = plt.axes()
    ax.set_axis_off()
    ax.imshow(cells[:, 1:-1], interpolation='none', cmap='RdPu')
    plt.savefig(f"resultat_{num_config:03d}.png", dpi=100, bbox_inches='tight')
    plt.close()

def calc_cell(num_config):
    cells = np.zeros((nb_iterations, nb_cellules+2), dtype=np.int16) #Matriz 360*362
    cells[0, (nb_cellules+2)//2] = 1 #La mitad de la matriz cells es 1
    for iter in range(1, nb_iterations):
        vals = np.left_shift(1, 4*cells[iter-1, 0:-2]
                            + 2*cells[iter-1, 1:-1]
                            + cells[iter-1, 2:])
        cells[iter, 1:-1] = np.logical_and(np.bitwise_and(vals, num_config), 1)
    return cells    

num_config = 0
if rank == 0:
    deb=time.time()
    for i in range(1,size):
        data = calc_cell(num_config)
        comm.send(data, dest=i, tag=num_config)
        num_config += 1
    
    while num_config < nombre_cas:
        data = calc_cell(num_config)
        comm.send(data, dest=i, tag=num_config)
        num_config += 1
    
    num_config = -1 
    
    for i in range(1,size):
        comm.send([0,0], dest=i)
    
    fin = time.time()
    print("rank ", rank, f"Temps de calcul des resultats : {fin-deb} secondes\n")
     

else:
    num_config = 0
    deb=time.time()
    while num_config < nombre_cas:
        cells = np.zeros((nb_iterations, nb_cellules+2), dtype=np.int16)
        Stat=MPI.Status()
        data=comm.recv(source=0, tag=MPI.ANY_TAG, status=Stat)
        num_config = Stat.Get_tag()
        if len(data)!=nb_iterations:
            break
        save_as_md(data, num_config)
    fin = time.time()
    print("rank ", rank, f"Temps d'affichage des resultats : {fin-deb} secondes\n")
     