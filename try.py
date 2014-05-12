#! /usr/bin/env python

import settings
from settings import log
from ndn_flow import ShotConsumer
import sys
import argparse
import os.path
import sys
#from pyndn import Name, Key
from pyndn import _pyndn
import pyndn
import logging
import datetime

import os.path
import signal
import math

ADAPTIVE_MOD_FLAG = "<adaptive>" #this is embeded in Interest.name to tell consumer the data_size which is recommended by consumer

producers = ["j06",  "tbed", "super", "h243","seu", "l07",  "telcom"]
producers = ["local", "l07", "super",  "tbed", "telcom", "j06","h243", "seu"]
liveps = []
deadps = []
triedps = []
#producers = ["j06",  "l07",  "telcom"]
#producers = ["telcom"]


        
    
def signal_handler(signal, frame):
    print 'You pressed Ctrl+C! to stop the program'
    log.info("%s have been detected, among those:" %(triedps))
    log.info("live producers: %s" %(liveps))
    log.info("dead producers: %s" %(deadps))
    
    sys.exit()
             
def go(args, **kwargs):
    #return
    global liveps
    global deadps
    global triedps
    for producer in producers:
        triedps.append(producer)
        if args.keep:
            consumer = ShotConsumer(Id='detect-alive-%s' %(producer), name="/%s/chunksize/dir/%s" %(producer, args.dstfile), turn=-1)
        else:
            consumer = ShotConsumer(Id='detect-alive-%s' %(producer), name="/%s/chunksize/dir/%s" %(producer, args.dstfile), turn=args.turn)
        consumer.start()
        
        
        if consumer.is_all:
            liveps.append(producer)
        else:
            deadps.append(producer)
    
    log.info("live producers: %s" %(liveps))
    log.info("dead producers: %s" %(deadps))
    
    
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(description='Configure the arguments of this program')
    parser.add_argument("-k", "--keep", help="Keep sending Interest until the back comes back. Cannot Trigger with -t", dest="keep", action='store_true')
    parser.add_argument("-t", "--turn", help="Try <N> turns at most, default is 5. If -k is set, this value is invalid", default=3)
    parser.add_argument("-f", "--dstfile", help="The remote file the program is about to fetch, default is img.jpg", default="b")
    parser.add_argument("-w", "--windowsize", help="the window size fixed to send packet, default is 1", default=1)
    
    args = parser.parse_args()
    

    
    #args.windowsize = int (args.windowsize)
    
#     print type(args.producer), args.producer
#     print type(args.dstfile), args.dstfile
#     print type(args.fixsize), args.fixsize
#     print type(args.windowsize), args.windowsize
    print type(args.keep), args.keep
    print type(args.turn), args.turn
    
    go(args)
    







