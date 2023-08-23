# Raytracer python
from PIL import Image
import numpy as np
from numpy import linalg
import math
import time
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank() #Le nombre des processus
size = comm.Get_size() #Nombre total des processus dans le communicateur

class Ray:
    """
    Définition d'un rayon : origine du rayon et sa direction
    """
    def __init__(self, begPoint : 'np.ndarray[np.double]' , direction : 'np.ndarray[np.double]' ):
        self.origin    = begPoint
        self.direction = direction
        # Normalise le vecteur direction
        self.normalizeDirection()

    def normalizeDirection( self ):
        nrmDir = linalg.norm(self.direction)
        assert(nrmDir > 1.E-14)
        self.direction /= nrmDir

class Sphere:
    """
    Définition d'une sphère par son centre et son rayon (plus couleur, coefficient de réflection et de transparence)
    """
    def __init__(self, center : 'np.ndarray[np.double]', radius : float, colour : 'np.ndarray[np.double]', 
                 reflection : float = 0., transparency : float = 0., 
                 emission : 'np.ndarray[np.double]' = np.zeros(3,dtype=np.double)):
        self.center : 'np.ndarray[np.double]' = center
        self.radius : float      = radius
        self.sqrRadius : float   = radius**2
        self.colour : 'np.ndarray[np.double]' = colour
        self.reflection= reflection
        self.transparency = transparency
        self.emission = emission

    def intersection( self, ray : Ray ):
        """
        Calcul une intersection rayon-sphère en utilisant la solution géométrique
        """
        l = self.center - ray.origin
        tca = l.dot(ray.direction)
        if tca < 0 : return None
        d2  = l.dot(l) - tca * tca
        if d2 > self.sqrRadius : return None

        thc = math.sqrt(self.sqrRadius - d2)
        t0  = tca - thc 
        t1  = tca + thc

        return (t0, t1)
    
    def normal( self, point ):
        """
        Retourne la normale à la sphère pour le point donné
        """
        assert( abs((point - self.center).dot(point - self.center) - self.sqrRadius ) < 1.E-7 ) 
        return (point - self.center)/self.radius
    
    def info(self):
        return f"Sphere centre {self.center}, rayon {self.radius}"

class Plane:
    """
    Définition d'un plan comme obstacle par un point du plan et une normale au plan (plus couleur, coefficient reflection et transparence)
    """
    def __init__(self, origin : 'np.ndarray[np.double]', cnormal : 'np.ndarray[np.double]', colour : 'np.ndarray[np.double]', 
                 reflection : float = 0., transparency : float = 0., 
                 emission : 'np.ndarray[np.double]' = np.zeros(3,dtype=np.double) ):
        self.origin : 'np.ndarray[np.double]' = origin 
        self.colour = colour 
        self.reflection = reflection
        self.transparency = transparency
        self.emission : 'np.ndarray[np.double]' = emission
        self.cnormal : 'np.ndarray[np.double]'  = cnormal

        nrm = linalg.norm(self.cnormal)
        assert(nrm > 1.E-7)
        self.cnormal /= nrm

    def intersection( self, ray : Ray ):
        """
        Calcul intersection plan-rayon en utilisant solution géométrique
        """
        c = np.dot(ray.direction, self.cnormal)
        if c >= 0:
            return None
        d = ray.origin - self.origin
        t = -np.dot(d,self.cnormal) / c
        return (t,t)

    def normal( self, point ):
        """
        Retourne la normale au plan
        """
        return self.cnormal

class Light:
    """
    Classe abstraite représentant une lumière
    """
    def __init__(self, transmission : 'np.ndarray[np.double]' ):
        self.transmission : 'np.ndarray[np.double]' = transmission

    def intersection(self, ray : Ray ):
        """
        Par défaut, la lumière sera invisible
        """
        return None
    
class PointLight(Light):
    """
    Source de lumière assez petite pour être assimilable à un point
    """
    def __init__(self, transmission : 'np.ndarray[np.double]', coords : 'np.ndarray[np.double]'):
        super().__init__(transmission)
        self.coordinates : 'np.ndarray[np.double]' = coords

    def direction( self, point : 'np.ndarray[np.double]' ):
        """
        Calcul la direction de la lumière par rapport à un point
        """
        lightDir    = self.coordinates - point
        nrmLightDir = linalg.norm(lightDir)
        if nrmLightDir > 1.E-14 :
            lightDir /= nrmLightDir
        return lightDir

class DirectionLight(Light):
    """
    Source de lumière assez éloignée pour que la direction du rayon lumineux peut être considéré comme constant
    """
    def __init__(self, transmission : 'np.ndarray[np.double]', dir : 'np.ndarray[np.double]' ):
        super().__init__(transmission)
        nrmDir = linalg.norm(dir)
        assert(nrmDir > 1.E-7)
        self.dir : 'np.ndarray[np.double]' = dir/nrmDir

    def direction( self, _unused : 'np.ndarray[np.double]' ):
        return -self.dir

MAX_RAY_DEPTH = 5
background    = np.zeros(3, dtype=np.double)
bias          = 1.E-4

def mix(a : float, b : float, mix : float) :
    return b * mix + a * (1 - mix)

def trace( ray : Ray, depth : int, objects ):
    """
    Calcul partiel de la couleur d'un pixel à partir d'un rayon (soit de la caméra, soit d'un autre objet, etc.)
    """
    inside  = False
    surfaceColor = np.zeros(3, dtype=np.double)
    nearestObj = None 
    tnearest = math.inf

    for obj in objects:
        intersection = obj.intersection(ray)
        if intersection is not None:
            t0,t1 = intersection
            if t0 < 0 : t0 = t1
            if t0 < tnearest : 
                tnearest = t0
                nearestObj = obj
    if nearestObj is None : return background # Si pas d'intersection

    # Calcul du point d'intersection
    point_hit  = ray.origin + tnearest * ray.direction
    normal_hit = nearestObj.normal(point_hit)

    # Test si on a intersecté l'objet par l'"intérieur"
    if ray.direction.dot(normal_hit) > 0 : 
        normal_hit = -normal_hit 
        inside = True

    if ((nearestObj.transparency > 0) or (nearestObj.reflection > 0)) and depth < MAX_RAY_DEPTH:
        facingRatio = -ray.direction.dot(normal_hit)
        reflection  = np.zeros(3, dtype = np.double)
        refraction  = np.ones (3, dtype = np.double)
        # Change la valeur de mixage pour déclencher l'effet :
        fresnelEffect = mix( (1 - facingRatio)**3, 1, 0.1)
        # Calcul la direction de réflexion (pas besoin de normaliser car tous les vecteurs sont normalisés)
        reflectionRay = Ray( point_hit + bias * normal_hit, ray.direction - 2 * ray.direction.dot(normal_hit) * normal_hit)
        reflection    = trace( reflectionRay, depth + 1, objects)

        # Si l'objet est transparent, on doit calculer le rayon de réfraction (transmission)
        if nearestObj.transparency > 0:
            ior  = 1.1
            eta  = ior if inside else 1./ior # Selon qu'on soit à l'intérieur ou à l'extérieur de l'objet
            cosi = -normal_hit.dot(ray.direction)
            k    = max(0.,1. - eta * eta * (1 - cosi * cosi))
            
            refractionRay = Ray(point_hit - bias * normal_hit, eta * ray.direction + (eta * cosi - math.sqrt(k)) * normal_hit)
            refraction    = trace( refractionRay, depth + 1, objects)
        # Le résultat est un mixte entre la réflection et la réfraction (si l'objet est transparent)
        surfaceColor = fresnelEffect * reflection + (1 - fresnelEffect) * nearestObj.transparency * refraction * nearestObj.colour
    else:
        # Ce n'est qu'un objet qui diffuse, pas besoin de générer un autre rayon
        for obj in objects :
            if isinstance(obj, Light):
                # Cet objet est une lumière, donc contribue à la diffusion de l'objet
                transmission   = np.ones(3, dtype=np.double)
                lightDirection = obj.direction( point_hit )
                # On vérifie qu'il n'y a pas d'obstacle entre la source de lumière et  la partie de l'objet dont on veut calculer l'éclairage
                for obj2 in objects:
                    if obj2 is not obj :
                        lightRay =  Ray( point_hit + bias * normal_hit, lightDirection )
                        intersect = obj2.intersection( lightRay )
                        if intersect is not None: # Si cet objet masque la lumière pour notre objet :
                            if intersect[0] > 0 or intersect[1] > 0:
                                transmission = np.zeros(3, dtype=np.double)
                                break
                surfaceColor += max(0., normal_hit.dot(lightDirection)) * obj.transmission * nearestObj.colour * transmission
    
    return surfaceColor + nearestObj.emission

def render( scene ) :
    """
    Fonction principale de rendu. On calcule un rayon allant de la camera à chaque pixel de l'image (assimilable à un plan dans l'espace 3D),
    fait un suivi de ce rayon et retourne une couleur par pixel. Si le rayon touche un obstacle, on retourne la couleur de l'obstacle calculée
    par rapport aux lumières et aux propriétés physiques de l'obstacle.
    """
    # Format de l'objet : Si le calcul de l'image prend trop longtemps sur votre ordinateur, vous pouvez modifier width et height
    # Par exemple, prendre 320, 200 ou 640, 480
    width, height = 320, 200 # 1280, 1024
    pixels = np.empty( (height, width, 3), dtype = np.float32)
    invWidth, invHeight = 2./width, 2./height
    # Paramètres de la caméra
    fov = 30.
    aspectRatio = width/height
    angle = math.tan(math.pi * 0.5 * fov / 180. )

    if rank ==0: # Maitre
        tdeb = time.time()
        task=0

        for i in range(1,size):
            comm.ssend(task,dest=i)
            task += 1

        row = np.empty((width,3), dtype=np.float32)
        stat = MPI.Status()
        while task < height:
            #Recibir es bloqueante porque debe recibir antes de enviar
            data = comm.Recv(row, status=stat)
            req=comm.isend(task, stat.Get_source())
            pixels[stat.Get_tag(),:] = row[:]
            req.wait(None)
            task += 1

        task = -1

        #Para recibir la ultima tanda de tareas, porque el while anterior ya cerro
        for i in range(1,size):
            #Envio de -1 para cortar la comunicacion en nodos esclavos
            data = comm.Recv(row, status=stat)
            req = comm.isend(task, stat.Get_source())
            pixels[stat.Get_tag(),:] = row[:]
            req.wait(None)

        tfin = time.time()
        print(f"Temps pris pour calculer l'image : {tfin-tdeb} secondes", "sur rank ", rank)
        # Sauvegarde de l'image calculée 
        if rank ==0:
            formatted = (pixels * 255).astype('uint8')
            image = Image.fromarray(formatted)
            image.save("scenedym.png")
        
    else:
        tdeb = time.time()
        task=0
        row = np.empty((width,3), dtype=np.float32)
        stat = MPI.Status()
        while task >= 0:
            task=comm.recv(source=0, status=stat)
            if task >=0:
                yy = (1 - ((task + 0.5) * invHeight)) * angle
                for ix in range(width):
                    # Calcul du rayon partant de la caméra et frappant le pixel dont on veut calculer la couleur
                    xx = (((ix + 0.5) * invWidth) - 1)  * angle * aspectRatio
                    ray = Ray( np.zeros(3,dtype=np.double), np.array([xx, yy, -1.]) )
                    row[ix] = trace(ray, 0, scene )
                    #print(ix, " trace ", trace(ray, 0, scene ))

                #Debe ser un send bloqueante
                comm.Send(row, 0, task)

        tfin = time.time()
        print(f"Temps pris pour calculer l'image : {tfin-tdeb} secondes ", "sur rank ", rank)


"""
Fonction principale : on crée une scène composée de sphères et d'une lumière
Une fois que la scène est complètement décrite, on appelle la fonction render
pour calculer le rendu de la#scène.
"""
scene = [
    Plane(np.array([0.,-4.1,0.]), np.array([0.,1.,0.]), np.array([1.,0.75,1.]), reflection=0.25),
    Plane(np.array([0.,0.,-25.]), np.array([0.,0.,1.]), np.array([0.75,0.75,0.75])),

    Sphere(np.array([0.,0.,-23.]), 4., np.array([1.,1.,1.])),
    Sphere(np.array([3.,4.,-23.25]), 1., np.zeros(3,dtype=np.double)),
    Sphere(np.array([-3.,4.,-23.25]), 1., np.zeros(3,dtype=np.double)),
    Sphere(np.array([ 2.,0., -20.]), 0.9, np.zeros(3,dtype=np.double), reflection=0.2),
    Sphere(np.array([-2.,0., -20.]), 0.9, np.zeros(3,dtype=np.double), reflection=0.2),

    Sphere(np.array([ 2.,0., -19.1]), 0.25, np.ones(3,dtype=np.double)),
    Sphere(np.array([-2.,0., -19.1]), 0.25, np.ones(3,dtype=np.double)),

    Sphere(np.array([ 2.,0., -20.]), 1.2, np.ones(3,dtype=np.double), transparency=0.9, reflection=0.5),
    Sphere(np.array([-2.,0., -20.]), 1.2, np.ones(3,dtype=np.double), transparency=0.9, reflection=0.5),
    Sphere(np.array([ 0.,-1.5, -20.]), 1., np.zeros(3,dtype=np.double), reflection=0.2),

    DirectionLight( np.array([1.,0.,0.]), np.array([ 1., -1., -1.])),
    DirectionLight( np.array([0.,0.,1.]), np.array([-1., -1., -1.])),
    PointLight( np.array([0.,1.,0.]), np.array([0.,10.,-15.]))
]

render(scene)
