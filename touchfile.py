#! /usr/bin/python
import sys

def usage():
    s= '''
        python touchfile <FILE_SIZE> [FILE_NAME]
        e.g.: python touchfile 1000
        e.g.: python touchfile 1000 x

        FILE_SIZE: size of generated file

        FILE_NAME: the name of generated file, default g
        '''
    print s

if __name__== "__main__":
    if len(sys.argv) <2:
        usage()
        exit(1)
    fsize = int(sys.argv[1])
    fname = "g"
    if len(sys.argv) == 3:
        fname = sys.argv[2]

    cnt = 0
    f = open(fname, "wb")
    while cnt < fsize:
        s = str(cnt) + "G"
        f.write(s)
        cnt += len(s)
