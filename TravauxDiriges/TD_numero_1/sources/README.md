
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

*Expliquer comment est compilé le code (ligne de make ou de gcc) : on aura besoin de savoir l'optim, les paramètres, etc. Par exemple :*

`make TestProductMatrix.exe && ./TestProductMatrix.exe 1024`


  ordre           | time    | MFlops  | MFlops(n=2048) 
------------------|---------|---------|----------------
i,j,k (origine)   | 2.73764 | 782.476 |                
j,i,k             |  |  |    
i,k,j             |  |  |    
k,i,j             |  |  |    
j,k,i             |  |  |    
k,j,i             |  |  |    


*Discussion des résultats*



### OMP sur la meilleure boucle 

`make TestProductMatrix.exe && OMP_NUM_THREADS=8 ./TestProductMatrix.exe 1024`

  OMP_NUM         | MFlops  | Temps |
------------------|---------|---------|
1                 | 503.884 | 4.26 seg 
2                 | 427.213 | 5.026 seg
4                 | 500.031 | 4.29 seg
6                 | 470.95 | 4.55 seg





### Produit par blocs

`make TestProduct.exe && ./TestProduct.exe 1024`

  szBlock         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
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
