#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>

void usage() {
  printf("Usage : main [input file path]");
}

#define LINEL 16
#define LINES 10000000

int main(int argc, char** argv) {
  if (argc < 2) usage();
  FILE* pFile = NULL;
  char buffer[100] = {0};
  char* b = buffer; 
  pFile = fopen(argv[1], "r+");
  if (pFile!=NULL)
  {
    for (int i = 0; i < LINES; i+= 1) {
	b = buffer;
	fgets (b , LINEL, pFile);
    }
    fclose (pFile);
  }
  return 0;
}
