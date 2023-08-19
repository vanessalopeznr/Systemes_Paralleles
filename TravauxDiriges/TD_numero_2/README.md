# TP2 de NOM Prénom

`pandoc -s --toc tp2.md --css=./github-pandoc.css -o tp2.html`





## Mandelbrot 

Se realiza una reparticion 

           | Taille image : 800 x 600 | 
-----------+-----------+---------------------------
séquentiel | 3.66      | 1       
1          | 0.039     |         
2          | 1.9       | 1.8      
3          |       
4          | 1.2       | 3     
5          | 
6          |             

Con 2 nodos, la velocidad del algoritmo es el doble del secuencial, lo hizo en la mitad del tiempo.
Con 4 nodos, la velocidad del algoritmo es 3 veces mas rapido que el secuencial.

*Expliquer votre stratégie pour faire une partition dynamique des lignes de l'image entre chaque processus*

Si el modulo entre la division height y el npb es mayor que el rank evaluado, se agrega 1 a la reparticion equitativas. Este 1 se agrega a todos los procesos hasta repartir el modulo entre el numero total de procesos; sino simplemente el rango es la reparticion equitativa.

Ej. 80 tiene modulo 2 cuando se divide por 3 procesos, entonces el va a repartir 2 unos en los dos primeros procesos.

y como los for recorren desde start hasta end-1, no hay problema de que un nodo tenga el numero de incio del final de otro 

## Produit matrice-vecteur



*Expliquer la façon dont vous avez calculé la dimension locale sur chaque processus, en particulier quand le nombre de processus ne divise pas la dimension de la matrice.*
