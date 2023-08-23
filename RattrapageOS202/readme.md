# Rattrapage Aout 2023 : Raytracer parallèle

Le but de cet examen est de paralléliser un programme créant des images de synthèse à partir d'un algorithme de raytracing écrit en python 3.

Pour avoir un code simple, ce raytracer ne gère que

* des solides sous forme de sphères et de plans dont on peut spécifier la couleur, le taux de transparence ou de réflexivité
* des lumières uniquement ponctuelles ou directionnelles dont on peut spécifier la couleur de la lumière émise.

Le script python contient déjà une scène décrite dans le programme principal.

## Prérequis

Le script python utilise `numpy` (*a priori* déjà installé sur votre machine) et `pillow`

Vous pouvez vérifier que pillow est installé sur votre machine en tapant dans un terminal :

    `python3 -c "import PIL"`

Si python vous rend la main sans afficher de message, c'est que pillow est déjà installé dans votre machine.

Dans le cas contraire, pour installer pillow :

* soit **vous êtes administrateur** de votre machine ou **utilisez un environnement virtuel** comme anaconda et dans ce cas
  `pip3 install pillow`
  devrait suffire, soit vous n'êtes qu'utilisateur de votre machine,
* soit **vous êtes simple utilisateur** est dans ce cas il faut taper :
  `pip3 install --user pillow`
  ce qui installera dans le module dans votre répertoire personnel

## Principe d'un algorithme de Raytracing

Le principe d'un algorithme de Raytracing est simple : on définit un observateur (la caméra) situé ici en *(0,0)* et dirigé selon l'axe *-Oz,*

et une zone rectangulaire se trouvant devant la caméra (à une distance définit selon l'angle d'ouverture de la caméra, fixée ici). La zone rectangulaire représente l'espace image et on décompose cette zone en pixels. 

Pour chaque pixel, on va lancer un rayon partant de la caméra et traversant le centre de ce pixel, puis chercher si ce rayon intersecte un ou plusieurs objets de la scène. Si le rayon ne traverse aucun objet de la scène, on donner la couleur du fond au pixel, sinon on regarde quel est l'objet dont l(intersection est la plus proche de ce pixel dans l'espace 3D. Si cet objet n'est ni transparent ni réflexif (on le dit seulement diffus), on calcule alors tous les rayons partant de cette intersection et les différentes sources de lumière. Si un de ces rayons n'intersecte pas avec un autre objet solide de la scène, alors on rajoute la contribution de cette lumière à la couleur du pixel en fonction du degrè d'incidence du rayon lumineux : 

    col = couleur sphère x transmission x max(0,<n|d>) x couleur lumière

où *n* est la normale par rapport au solide au point d'intersection du rayon lancé par la caméra et d la direction du rayon partant de cette intersection et se dirigeant vers la source lumineuse.

![1692427554569](image/readme/1692427554569.png)

Si le solide est transparent ou réflechit, le calcul est un peu plus compliqué car il faut dans ce cas suivre le rebond ou la diffraction du rayon sur le solide afin de calculer la couleur du pixel. Le calcul peut donc dans ce prendre bien plus de temps que si le rayon issu de la caméra ne rencontre qu'un solide mate.

## Présentation du programme

La scène décrivant l'image à produire est décrite sous forme d'une liste d'objets (solides et lumières) dans une liste python dans le programme principal.

Une fonction `render` mise en oeuvre plus haut est la fonction principale du script. Elle définit le format de l'image (que vous pouvez modifier si le format par défaut implique sur votre machine un temps de restitution trop long), puis calcule et sauvegarde l'image  produite. Elle utilise intensivement une fonction `trace` qui se charge pour chaque pixel de suivre le rayon correspondant et d'en calculer la couleur associée.

Différentes classes ont été mise en oeuvre pour décrire les différentes formes géométriques permises pour les solides ou les lumières.

## Travaille à rendre

Pour chaque parallélisation demandée, on écrira un script différent. Il faudra donc rendre deux scripts pythons et un document texte (markdown, pdf, word, etc. ) à la fin de l'examen.

### Matériel utilisé

Indiquez dans votre document le nombre de coeurs de calcul physiques et logiques de votre ordinateur.

### Parallélisation naïve

Dans un premier temps, on parallélisera, avec mpy4py, l'algorithme de raytracing naïvement en partitionnant statiquement la charge de travail sur les processus. 

* Mettre en oeuvre la parallélisation statique
* Calculer le speed-up obtenu

* Interprétez vos résultats au vu de l'algorithme de raytracing et de la parallélisation effectuée

### Parallélisation dynamique

On mettra en oeuvre cette fois ci une parallélisation dynamique à l'aide d'un algorithme maître-esclave.

* Mettez en oeuvre la parallélisation
* Calculer le speed-up obtenu
* Comparez et interprétez vos résultats en les comparants avec les résultats de la parallélisation naïve.
