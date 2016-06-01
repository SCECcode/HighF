FC=gfortran -O3
CC=gcc -O3

all:	BBPtoSAC copy

clean:
	rm -f *.o BBPtoSAC

BBPtoSAC:	BBPtoSAC.f sacio.o
	$(FC) -o BBPtoSAC BBPtoSAC.f sacio.o

sacio.o: sacio.c
	$(CC) -c sacio.c

copy:
	cp BBPtoSAC ../bin
