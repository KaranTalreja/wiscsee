WORLOADS = CReadTest CWriteTest

default : $(WORLOADS)

CReadTest : CReadTest.c
	g++ -g $< -o $@

CWriteTest : CWriteTest.c
	g++ -g $< -o $@

clean:
	-rm $(WORLOADS)
