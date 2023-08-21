# TD n°3 - parallélisation du Bucket Sort

*Ce TD peut être réalisé au choix, en C++ ou en Python*

Implémenter l'algorithme "bucket sort" tel que décrit sur les deux dernières planches du cours n°3 :

- le process 0 génère un tableau de nombres arbitraires,
- il les dispatch aux autres process,
- tous les process participent au tri en parallèle,
- Les medians sont envoyées au process 0
- Le process 0 trie les médianes et envoie les limites de chaque bucket aux process

           | Taille array | Time
-----------+--------------+----------
séquentiel | 90000000     | 5.4   
1          |              |   
2          |              |      
3          |              |
4          |              |     
5          |              |
6          |              |

