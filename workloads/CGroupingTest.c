#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include<sys/types.h>
#include<sys/stat.h>
#include<fcntl.h>
#include<string.h>
#include<pthread.h>

void usage() {
  printf("Usage : main [working dir]");
}

#define SLF_NUM 6

const char* shortLivedFiles[] = {"slf1", 
				 	"slf2",
				 	"slf3",
				 	"slf4",
				 	"slf5",
				 	"slf6",
				 	"slf7",
				 	"slf8",
				 	"slf9",
				 	"slf10",
				 	"slf11",
				 	"slf12"};

char* getPath (char* bufferPath, char* path, const char* name) {
  sprintf(bufferPath, "%s/%s", path, name);
  return bufferPath;
}

typedef struct {
  char* currPath;
  int i;
} args_t;

void* writeFileGoodGrouping(void* args) {
    char bufferPath[100];
    args_t* myArgs = (args_t*) args;
    printf("Writing %s\n", getPath(bufferPath, myArgs->currPath, shortLivedFiles[myArgs->i]));
    for (int n = 0; n < 100; n++) {
      FILE* fout = fopen(bufferPath, "w+");
      if (fout == NULL) perror("File not open");
      else {
        for (int i = 0; i < 1000; i++) {
          fputs(bufferPath, fout);
        }
        fsync(fileno(fout));
        unlink(bufferPath);
        fclose(fout);
      }
    }
    printf("Done with %d\n", myArgs->i);
}

void* writeFile(void* args) {
    char bufferPath[100];
    args_t* myArgs = (args_t*) args;
    printf("Writing %s\n", getPath(bufferPath, myArgs->currPath, shortLivedFiles[myArgs->i]));
    for (int n = 0; n < 100*myArgs->i; n++) {
      FILE* fout = fopen(bufferPath, "w+");
      if (fout == NULL) perror("File not open");
      else {
	for (int j = 0; j < 100*myArgs->i; j++) {
          for (int i = 0; i < 1000*myArgs->i; i++) {
            fputs(bufferPath, fout);
          }
	  fseek(fout, 0L, SEEK_SET);
	}
        fsync(fileno(fout));
        unlink(bufferPath);
        fclose(fout);
      }
    }
    printf("Done with %d\n", myArgs->i);
}

int main(int argc, char** argv) {
  if (argc < 2) usage();
  const char* sld = "shortLivedDir";
  char bufferPath[100];
  mkdir(getPath(bufferPath, argv[1], sld), 0777);
  char* currPath = strdup(bufferPath);
  int fd = open(bufferPath, O_DIRECTORY | O_RDONLY);
  pthread_t* threads = (pthread_t*)malloc(SLF_NUM*sizeof(pthread_t));
  for (int i = 0; i < SLF_NUM; i++) {
    args_t* args = (args_t*)malloc(sizeof(args_t));
    args->i = i;
    args->currPath = currPath;
    pthread_create(&threads[i], NULL, writeFile, args);
  }
  for (int i = 0; i < SLF_NUM; i++) {
    pthread_join(threads[i], NULL);
  }
  fsync(fd);
  return 0;
}
