# Calcul de l'ensemble de Mandelbrot en python
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
import time
import matplotlib.cm
# Run: mpirun -np 2 python3 mpi-python.py 

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank() #Le nombre des processus
size = comm.Get_size() #Nombre total des processus dans le communicateur

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius : float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c:complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c,smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) -> int | float :
        z    : complex
        iter : int

        # On vérifie dans un premier temps si le complexe
        # n'appartient pas à une zone de convergence connue :
        #   1. Appartenance aux disques  C0{(0,0),1/4} et C1{(-1,0),1/4}
        if c.real*c.real+c.imag*c.imag < 0.0625 :
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        #  2.  Appartenance à la cardioïde {(1/4,0),1/2(1-cos(theta))}    
        if (c.real > -0.75) and (c.real < 0.5) :
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2,1.E-14)):
                return self.max_iterations
        # Sinon on itère 
        z=0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

def non_paral():

    # On peut changer les paramètres des deux prochaines lignes
    mandelbrot_set = MandelbrotSet(max_iterations=50,escape_radius=10)
    width, height = 1024, 1024

    scaleX = 3./width
    scaleY = 2.25/height
    convergence = np.empty((height,width),dtype=np.double)

    # Calcul de l'ensemble de mandelbrot :
    deb = time.time()
    for y in range(height):
        for x in range(width):
            c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
            convergence[x,y] = mandelbrot_set.convergence(c,smooth=True)

    fin = time.time()

    print(f"Temps du calcul de l'ensemble de Mandelbrot : {fin-deb}") 

    # Constitution de l'image résultante :
    deb=time.time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T)*255))
    fin = time.time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    #image.show()
    image.save('mandelbrot.png')

def paral_mod_0(): # SOLO CON PROCESOS EL CUAL LA DISTRIBUCION ES MODULO 0 
    
    # On peut changer les paramètres des deux prochaines lignes
    mandelbrot_set = MandelbrotSet(max_iterations=50,escape_radius=10)
    width, height = 1024, 1024

    scaleX = 3./width
    scaleY = 2.25/height

    #Divise la matrix en dependant du nombres de coeurs
    if height%size > rank:
        salto = height//size + 1
        start = rank*salto
    else:
        salto = height//size
        start = (rank*salto)+height%size
    
    end=start+salto

    convergence = np.empty((height,width),dtype=np.double)
    convergence = convergence.copy(order='C')
    print((salto,width), rank, start, end, end-start)

    # Calcul de l'ensemble de mandelbrot :
    deb = time.time()
    for y in range(start,end): #Van desde start hasta end-1
        for x in range(width):
            c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
            convergence[y,x] = mandelbrot_set.convergence(c,smooth=True)

    if rank==0:
        recvbuf = np.empty((width,height),dtype=np.double)
    else:
        recvbuf=None

    comm.Gatherv(convergence[start:end,:],recvbuf, root=0)


    if rank != 0:
        fin = time.time()
        print(f"Temps de constitution de l'image : {fin-deb}")
    if rank==0:
        # Constitution de l'image résultante :
        deb=time.time()
        image = Image.fromarray(np.uint8(matplotlib.cm.plasma(recvbuf)*255))
        fin = time.time()
        print(f"Temps de constitution de l'image : {fin-deb}")
        image.save('mandelbrot2.png')
    
def paral(): # SOLO CON TODOS LOS NUMEROS DE PROCESOS 

    # On peut changer les paramètres des deux prochaines lignes
    mandelbrot_set = MandelbrotSet(max_iterations=50,escape_radius=10)
    width, height = 1024, 1024

    scaleX = 3./width
    scaleY = 2.25/height

    #Divise la matrix en dependant du nombres de coeurs
    if height%size > rank:
        salto = height//size + 1
        start = rank*salto
    else:
        salto = height//size
        start = (rank*salto)+height%size
    
    end=start+salto

    convergence = np.empty((height,width),dtype=np.double)

    # Calcul de l'ensemble de mandelbrot :
    deb = time.time()
    for y in range(start,end): #Van desde start hasta end-1
        for x in range(width):
            c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
            convergence[y,x] = mandelbrot_set.convergence(c,smooth=True)

    if rank==0:
        recvbuf = np.empty((width,height),dtype=np.double)
    else:
        recvbuf=None

    # Collect local array sizes using the high-level mpi4py gather
    shapee=np.empty((salto,width),dtype=np.double)
    shapee=convergence[start:end,:]

    #comm.Gatherv(sendbuf=shapee, recvbuf=(recvbuf, sendcounts, displs, MPI.DOUBLE), root=0)
    comm.Gatherv(sendbuf=shapee, recvbuf=(recvbuf, shapee.shape[0]*shapee.shape[1]), root=0)
    
    #comm.Gatherv(convergence[start:end,:],recvbuf, root=0)

    fin = time.time()
    print("Rank ", rank,f" Temps de constitution de l'image : {fin-deb}")
    if rank==0:
        # Constitution de l'image résultante :
        deb=time.time()
        image = Image.fromarray(np.uint8(matplotlib.cm.plasma(recvbuf)*255))
        fin = time.time()
        print(f"Temps de constitution de l'image : {fin-deb}")
        image.save('mandelbrot.png')
   
def paral_maestro_esclavo():

    # On peut changer les paramètres des deux prochaines lignes
    mandelbrot_set = MandelbrotSet(max_iterations=50,escape_radius=10)
    width, height = 1024, 1024

    scaleX = 3./width
    scaleY = 2.25/height

    if rank==0: # Maitre
        deb=time.time()
        convergence = np.empty((height,width),dtype=np.double)
        task=0

        for i in range(1,size):
            #Ssend al incio para garantizar la comunicacion con todos los procesos (sino las tareas no se terminan de enviar a los procesos y un proceso toma la delantera y solo trabaja el jaja)
            comm.ssend(task,dest=i)
            task += 1

        row = np.empty(width, dtype=np.double)
        stat = MPI.Status()
        while task < height:
            #Recibir es bloqueante porque debe recibir antes de enviar
            data = comm.Recv(row, status=stat)
            req=comm.isend(task, stat.Get_source())
            convergence[stat.Get_tag(),:] = row[:]
            req.wait(None)
            task += 1

        task = -1

        #Para recibir la ultima tanda de tareas, porque el while anterior ya cerro
        for i in range(1,size):
            #Ya no necesito enviar nada
            data = comm.Recv(row, status=stat)
            print(task)
            #req = comm.isend(task, stat.Get_source())
            convergence[stat.Get_tag(),:] = row[:]
            #req.wait(None)
        fin = time.time()
        print("rank ", rank, f"Temps de calcul mandelbrot pour esclave : {fin-deb} secondes\n")

        deb=time.time()
        image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence)*255))
        fin = time.time()
        print(f"Temps de constitution de l'image : {fin-deb}")
        image.save('mandelbrot.png')
              
    else:
        deb=time.time()
        task = 0
        row = np.empty(width, dtype=np.double)
        stat = MPI.Status()
        while task >= 0:
            task=comm.recv(source=0, status=stat)
            if task >=0:
                for x in range(width):
                    c = complex(-2. + scaleX*x, -1.125 + scaleY * task)
                    row[x] = mandelbrot_set.convergence(c,smooth=True)

                #Debe ser un send bloqueante, ya que si envio y el rank 0 ya me esta asignando otra tarea, se enloquece
                comm.Send(row, 0, task)
        fin = time.time()
        print("rank ", rank, f"Temps de calcul mandelbrot pour esclave : {fin-deb} secondes\n") 
#non_paral()
#paral()
paral_maestro_esclavo()