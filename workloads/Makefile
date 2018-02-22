WORLOADS = CReadTest CWriteTest CReadTestSeq CGroupingTest CWriteTestFsync

default : $(WORLOADS)

CGroupingTest : CGroupingTest.c
	g++ -g $< -o $@ -lpthread

CReadTest : CReadTest.c
	g++ -g $< -o $@

CReadTestSeq : CReadTestSeq.c
	g++ -g $< -o $@

CWriteTestFsync : CWriteTestFsync.c
	g++ -g $< -o $@

CWriteTest : CWriteTest.c
	g++ -g $< -o $@

clean:
	-rm $(WORLOADS)
