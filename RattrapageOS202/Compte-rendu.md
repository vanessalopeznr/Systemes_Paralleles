# Caractéristiques du système

- Coeurs physiques : 6
- Coeurs logiques : 12
- L2 : 7.5 MiB (6 instances)
- L3 : 12 MiB (1 instance)

# Solution

J'ai travaillé sur une taille d'image de 320 x 200 pour accélérer le processus d'exécution du programme. 

## Parallélisation naïve

Le programme complété se trouvé dans le dépôt sous le nom ``paral_naive.py`` et génère l'image scenenaiv.png

Pour la parallélisation native, dans un premier temps, une stratégie a été mise en place pour séparer les données en fonction du nombre de processus affectés à ce programme, puis la matrice de pixels a été divisée par colonnes et enfin, tout a été regroupé dans le cœur 0 pour obtenir l'image.

On a obtenu les resultats suivantes:

  Program         | Temps      | Speedup |
------------------|------------|---------|
Séquentiel        | 18.43 seg  | 1 
1                 | 18.34 seg  | 1
2                 | 12.33 seg  | 1.5
3                 | 9.07 seg   | 2.03
4                 | 8.3 seg    | 2.22
5                 | 7.01 seg   | 2.6
6                 | 5.3 seg    | 3.47

Un très bon résultat est obtenu, puisqu'avec le nombre maximum de cœurs dont dispose mon ordinateur, la parallélisation naïve permet de l'exécuter jusqu'à 3,4 fois plus vite que le programme séquentiel. 
Il y a aussi une bonne progression de l'accélération en fonction du nombre de cœurs utilisés, car elle augmente proportionnellement.

## Parallélisation dynamique

Le programme complété se trouvé dans le dépôt sous le nom ``paral_dynam.py`` et génère l'image scenedym.png

Pour la parallélisation dynamique, une stratégie maître-esclave a été mise en œuvre, dans laquelle le rang 0 envoie un index de tâche aux autres processeurs et ceux-ci effectuent le calcul d'une seule ligne, puis finalement, lorsque les processeurs effectuent le calcul de la ligne entière, ils envoient la ligne au processus 0 et demandent une nouvelle tâche. Cette opération est répétée jusqu'à ce que le nombre de colonnes soit atteint.

On a obtenu les resultats suivantes:

  Program         | Temps      | Speedup |
------------------|------------|---------|
Séquentiel        | 18.43 seg  | 1 
1                 | --         | --
2                 | 13.24 seg  | 1.4
3                 | 8.84 seg   | 2.08
4                 | 7.1 seg    | 2.6
5                 | 6.36 seg   | 2.9
6                 | 5.2 seg    | 3.54

De très bons résultats sont également obtenus, cependant, cet algorithme permet une accélération légèrement supérieure à la parallélisation native parce que contrairement à la parallélisation précédente, celle-ci ne doit pas attendre que les autres processeurs aient terminé leur tâche pour obtenir un résultat commun, par contre, chacun peut gérer ses propres temps.