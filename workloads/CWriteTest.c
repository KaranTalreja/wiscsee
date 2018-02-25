#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>

#define LINEL 16
#define LINES 10000000

void usage() {
  printf("Usage : CWriteTest [output file path]");
}

int main(int argc, char** argv) {
  if (argc < 2) usage();
  FILE* pFile = fopen(argv[1], "w+");
  char buffer[100] = {0};
  if (pFile!=NULL)
  {
    for (int i = 0; i < LINES; i++) {
        sprintf(buffer, "Line : %08d\n", i);
        fputs (buffer ,pFile);
//	fsync(fileno(pFile));
    }
    fclose (pFile);
  }
  return 0;
}
