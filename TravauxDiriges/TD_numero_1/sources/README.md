
# TD1

`pandoc -s --toc README.md --css=./github-pandoc.css -o README.html`





## lscpu

```
Architecture:            x86_64
  CPU op-mode(s):        32-bit, 64-bit
  Address sizes:         39 bits physical, 48 bits virtual
  Byte Order:            Little Endian
CPU(s):                  12
  On-line CPU(s) list:   0-11
Vendor ID:               GenuineIntel
  Model name:            12th Gen Intel(R) Core(TM) i7-1255U
    CPU family:          6
    Model:               154
    Thread(s) per core:  2
    Core(s) per socket:  6
    Socket(s):           1
    Stepping:            4
    BogoMIPS:            5222.41
    Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht sysca
                         ll nx pdpe1gb rdtscp lm constant_tsc rep_good nopl xtopology tsc_reliable nonstop_tsc cpuid pni pclmulqdq vmx
                          ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hyperviso
                         r lahf_lm abm 3dnowprefetch invpcid_single ssbd ibrs ibpb stibp ibrs_enhanced tpr_shadow vnmi ept vpid ept_ad
                          fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid rdseed adx smap clflushopt clwb sha_ni xsaveopt xsavec 
                         xgetbv1 xsaves avx_vnni umip waitpkg gfni vaes vpclmulqdq rdpid movdiri movdir64b fsrm serialize flush_l1d ar
                         ch_capabilities
Virtualization features: 
  Virtualization:        VT-x
  Hypervisor vendor:     Microsoft
  Virtualization type:   full
Caches (sum of all):     
  L1d:                   288 KiB (6 instances)
  L1i:                   192 KiB (6 instances)
  L2:                    7.5 MiB (6 instances)
  L3:                    12 MiB (1 instance)
Vulnerabilities:         
  Itlb multihit:         Not affected
  L1tf:                  Not affected
  Mds:                   Not affected
  Meltdown:              Not affected
  Mmio stale data:       Not affected
  Retbleed:              Mitigation; Enhanced IBRS
  Spec store bypass:     Mitigation; Speculative Store Bypass disabled via prctl and seccomp
  Spectre v1:            Mitigation; usercopy/swapgs barriers and __user pointer sanitization
  Spectre v2:            Mitigation; Enhanced IBRS, IBPB conditional, RSB filling, PBRSB-eIBRS SW sequence
  Srbds:                 Not affected
  Tsx async abort:       Not affected 
```

*Des infos utiles s'y trouvent : nb core, taille de cache*



## Produit matrice-matrice



### Permutation des boucles

Fonctionnement make command:

Lorsque le make est appellé, il cherche le fichier Makefile et lit qu'est c'est qu'il doit faire lors le command _TestProductMatrix.exe_ est appellé. Dans ce cas la, il fait: TestProductMatrix.cpp Matrix.hpp Matrix.cpp ProdMatMat.cpp avec le command CXX qui fait le reference à g++ -fopenmp précise sur le Make_linux.inc que l'on a importé plus tôt, les configurations et les libraries que sont necessaires pour ejecuter le program et ensuite, il execute le fichier déjà compile avec la taille de la matrix.

`make TestProductMatrix.exe && ./TestProductMatrix.exe 1024`

MFlops: Opérations en virgule flottante par seconde (Operaciones de coma flotante por segundo). Plus le nombre de flops est élevé, plus le nombre d'opérations par seconde augmente.

  ordre           | time    | MFlops  | MFlops(n=2048) 
------------------|---------|---------|----------------
i,j,k (origine)   | 3.69 | 580.709 |                 
j,i,k             | 4.05 | 529.398 |    
i,k,j             | 10.75 | 199.686 |    
k,i,j             | 13.35 | 160.845 |    
j,k,i             | 0.71 | 3005.81 |    
k,j,i             | 0.81 | 2647.08 |    


*Discussion des résultats*

Il est clair que les meilleures performances sont obtenues lorsque la boucle en i est
la plus interne. De plus, dans ce cas, la variation du temps de calcul en fonction de la
dimension de la matrice devient insignifiante. Les meilleures performances étant obtenues
avec les boucles dans l’ordre jki.

On sait que la matrice est stockée par colonne, on voit qu’en mettant la boucle en i comme la plus interne, cela permet d’accéder aux coefficients de C et de A en contigü dans la mémoire, tandis que pour B, on conserve la même valeur durant toute la boucle interne. En mettant k en boucle du milieu, cela
permet également d’accèder en contigü aux cœfficients de B.


En revanche, lorsque la boucle en j est la plus interne, on obtient les plus mauvais
performances puisque dans ce cas, l’accès aux cœfficients de C et de B se fait avec des
sauts mémoires dont la distance est égale à la dimension de la matrice.


### OMP sur la meilleure boucle 

Il faut mettre sur les bucles **#pragma omp parallel for collapse(3)** for parallelize le 3 bucles et avec le command:

`make TestProductMatrix.exe && OMP_NUM_THREADS=8 ./TestProductMatrix.exe 1024`

Si le command ne dit pas le nombre de threads, l'ordinateur prend tous les coeurs disponibles. (in my c ase 6)

  OMP_NUM         | MFlops  | Temps |
------------------|---------|---------|
1                 | 657.009 | 3.26 seg 
2                 | 1270.42 | 1.69 seg
4                 | 1921.46 | 1.12 seg
6                 | 2354.43 | 0.912 seg

ou c'est possible aussi préciser tous les instructions sur le ligne au code **#pragma omp parallel for num_threads(6) collapse(3)**

Il est inutile de prendre plus de coeurs sur l'ordinateur que j'utilise pour le TP, puisque ce dernier ne contient que six cœurs physiques de calcul.


### Produit par blocs

Il faut faire une fonction pour separer le code par blocs. Au debut, c'est necessaire inicializer la matrix C et apres faire 3 boucles pour parcourir les lignes et colonnes divisés par un constante déjà définie.

`make TestProduct.exe && ./TestProduct.exe 1024`

  szBlock         | MFlops(n=1024) | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
origine (=max)    |  |
32                |  |
64                |  |
128               |  |
256               |  |
512               |  | 
1024              |  |




### Bloc + OMP



  szBlock      | OMP_NUM | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)|
---------------|---------|---------|-------------------------------------------------|
A.nbCols       |  1      |         |                |                |               |
512            |  8      |         |                |                |               |
---------------|---------|---------|-------------------------------------------------|
Speed-up       |         |         |                |                |               |
---------------|---------|---------|-------------------------------------------------|



### Comparaison with BLAS


# Tips 

```
	env 
	OMP_NUM_THREADS=4 ./produitMatriceMatrice.exe
```

```
    $ for i in $(seq 1 4); do elap=$(OMP_NUM_THREADS=$i ./TestProductOmp.exe|grep "Temps CPU"|cut -d " " -f 7); echo -e "$i\t$elap"; done > timers.out
```
