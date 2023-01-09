CC = gcc
CLANGPP = clang++  -g
MPICC = mpicc
CXX = g++ 
MPICXX = mpic++
LIBMPI = -lmpi
MPIOPT = -oversubscribe
OMP = -fopenmp
INCPATH = -I/usr/include/x86_64-linux-gnu/openblas-pthread/

LIBPTHREAD = -lpthread
LIBPSTL    = -ltbb
TBB = -ltbb
BLAS= -lopenblas
SANITIZER= -fsanitize=address -fsanitize=undefined -fno-sanitize=null -fno-sanitize=alignment