# Calcul pi par une méthode stochastique (convergence très lente !)
import time
import numpy as np
import random

# Nombre d'échantillons :
nbSamples = 40000000

beg = time.time()
# Tirage des points (x,y) tirés dans un carré [-1;1] x [-1; 1]
#Crea puntos entre -1 y 1 de tamaño nbSamples
#x = 2.*np.random.random_sample((nbSamples,))-1.
#y = 2.*np.random.random_sample((nbSamples,))-1.
x = random.uniform(-1, 1)
y = random.uniform(-1, 1)

# Création masque pour les points dans le cercle unité
#Toma la ecuacion de un circulo x^2 + y^2 < 1 para evaluar si los puntos estan dentro del circulo
filtre = np.array(x*x+y*y<1.)
# Compte le nombre de points dans le cercle unité
#Suma los puntos que estan dentro del circulo con add y con reduce se escoge el eje 0 (por filas)
sum = np.add.reduce(filtre, 0)

approx_pi = 4.*sum/nbSamples
end = time.time()

print(f"Temps pour calculer pi : {end - beg} secondes")
print(f"Pi vaut environ {approx_pi}")

