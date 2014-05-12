#! /usr/bin/env python
import settings
import sys
#from pyndn import Name, Key
from pyndn import _pyndn
import pyndn

import datetime
import time
# from mydata import MyData, ChunkInfo
# from mydata import DEFAULT_CHUNK_SIZE, DEFAULT_RUN_TIMEOUT
# from mydata import ADAPTIVE_MOD_FLAG
# from mydata import CHUNK_ADDITIVE_INCREASEMENT_SIZE, CHUNK_MULTIPLICATIVE_DECREASEMENT_FACTOR, MAX_CHUNK_SIZE

from settings import log, ROOT_DIR

from ndn_flow import FlowConsumer

# from mydata import PACKET_HEADER_SIZE, CHUNK_HEADER_SIZE, PACKET_MTU
#from datetime import datetime
import os.path
import signal
import math
import argparse
from paper_kit import *

PAPER = "chunksize"

class MyConsumer(object):
    def __init__(self, args):
        self.args = args
        self.Id = args.Id or "test"
    def start(self): 
        args = self.args
        consumer = FlowConsumer(Id=self.Id, name="/%s/chunksize/dir/%s" %(args.producer, args.dstfile), fout=None, monitor_out_dir=None, 
                                       size_fix = args.fixsize,  window_fix = args.windowsize, rtt_fix=4.0)
        consumer.start()
        t = 0.0
        g = 0.0
        for a in consumer.chunkInfos:
            chunkinfo = a
            if chunkinfo.status == 2:
                assert chunkinfo.retxN >=1, "Illegal: retxN < 1"
                assert chunkinfo.endT != None, "Illegal: endT == None"
                t +=a.chunk_size * a.retxN
                g +=a.data_size
            else:
                print chunkinfo, "Warning !!!!!"
                
                
        i = (g/t)
        j = float(consumer.chunkSizeEstimator.lostN)/(consumer.chunkSizeEstimator.lostN + consumer.chunkSizeEstimator.receivedN)
        k = consumer.chunkSizeEstimator.get_loss_rate()
        print "G2T is %s" % i
        print "chunk loss rate is %s, receivedN is %s, lostN is %s" %(j, consumer.chunkSizeEstimator.receivedN, consumer.chunkSizeEstimator.lostN)
        print "packet loss rate is %s" %k
        
        fpath = os.path.join(settings.OUT_DATA_DIR, "g2t-%s.dat" %(settings.HOST))
        fout = open(fpath, "a")
        fout.write("chuklossrate=%s, packetlossrate=%s, g2t=%s, chunksize=%s, winsize=%s, file=%s, src=%s, dst=%s, beginT=%s, endT=%s\n" 
                   %(j, k, i, args.fixsize, args.windowsize, args.dstfile, settings.HOST, args.producer, consumer.mydata.beginT, consumer.mydata.endT))
        
        fout.flush()
        fout.close()
        if consumer.is_all:
            return True
        else:
            return False


if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description='Configure the arguments of this program')
    parser.add_argument("-p", "--producer", help="The producer name of this program, default is seu", default="local")
    parser.add_argument("-f", "--dstfile", help="The remote file the program is about to fetch, default is img.jpg", default="c")
    parser.add_argument("-s", "--fixsize", help="the chunk size fixed to the program, default is 1000", default=1000)
    parser.add_argument("-w", "--windowsize", help="the window size fixed to send packet, default is 1", default=20)
     
    args = parser.parse_args()
     
 
    if args.fixsize == "none" or args.fixsize == "None":
        args.fixsize = None
    else:
        args.fixsize = int (args.fixsize)
    args.windowsize = int (args.windowsize)
    args.Id = "test"
#     print type(args.producer), args.producer
#     print type(args.dstfile), args.dstfile
#     print type(args.fixsize), args.fixsize
#     print type(args.windowsize), args.windowsize
#     
    consumer = MyConsumer(args)
    consumer.start()
    log.info("end")
