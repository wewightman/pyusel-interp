compile: cubic.o
	gcc -Wall cubic.o main.c -o fuckit -lm
cubic.o: cubic.c cubic.h
	gcc -Wall -c cubic.c -lm
