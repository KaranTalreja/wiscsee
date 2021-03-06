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
  FILE* pFileLag = NULL;
  char buffer[100] = {0};
  char* b = buffer; 
  pFile = fopen(argv[1], "r+");
  pFileLag = fopen(argv[1], "r+");
  size_t Tline = 4096 / 2;
  size_t strideLen = 100;
  size_t inC = 0, outC = 0;
  if (pFile!=NULL)
  {
    for (int i = 0; i < LINES && outC < 698; i+= Tline*7) {
        outC++;
	fseek(pFile, (Tline)*LINEL*7, SEEK_CUR);
	b = buffer;
	fgets (b , LINEL, pFile);
	printf("%s\n", b);
	if (i > strideLen*Tline*7 && inC < 597) {
           inC++;
           fseek(pFileLag, (Tline)*LINEL*3, SEEK_CUR);
           b = buffer;
           fgets (b , LINEL, pFileLag);
           printf("%s\n", b);
	}
    }
    fclose (pFile);
    fclose (pFileLag);
    printf("%ld %ld\n", outC, inC);
  }
  return 0;
}
