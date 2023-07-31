from mpi4py import MPI
import numpy as np
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank() #Le nombre des processus
size = comm.Get_size() #Nombre total des processus dans le communicateur

# Nombre d'échantillons :
nbSamples = 40000000
nbSamplesparProc = nbSamples/size

beg = time.time()

if rank==0:
    x = 2.*np.random.random_sample((int(nbSamplesparProc),))-1.
    y = 2.*np.random.random_sample((int(nbSamplesparProc),))-1.
    filtre = np.array(x*x+y*y<1.)
    sum = np.add.reduce(filtre, 0)
    approx_pi = 4.*sum/int(nbSamplesparProc)

    for i in range(1,size):
        data = comm.recv(source=i,tag=1)
        approx_pi = approx_pi + data
    
    print("Pi vaut environ ",approx_pi)

else:
    x = 2.*np.random.random_sample((int(nbSamplesparProc),))-1.
    y = 2.*np.random.random_sample((int(nbSamplesparProc),))-1.
    filtre = np.array(x*x+y*y<1.)
    sum = np.add.reduce(filtre, 0)
    approx_pi = 4.*sum/int(nbSamplesparProc)
    comm.send(approx_pi,dest=0,tag=1)
    print("I am", rank," and Pi vaut environ ",approx_pi)

end=time.time()
print("Temps pour calculer pi : ",end-beg," secondes")