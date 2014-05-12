#! /usr/local/bin/python
import sys
#from pyndn import Name, Key
from pyndn import _pyndn
import pyndn
import logging
import datetime
from mydata import MyData, ChunkInfo, log
from mydata import DEFAULT_CHUNK_SIZE, DEFAULT_RUN_TIMEOUT
from mydata import ADAPTIVE_MOD_FLAG
from mydata import CHUNK_ADDITIVE_INCREASEMENT_SIZE, CHUNK_MULTIPLICATIVE_DECREASEMENT_FACTOR, MAX_CHUNK_SIZE

from ndn_flow import FlowConsumer

from mydata import PACKET_HEADER_SIZE, CHUNK_HEADER_SIZE, PACKET_MTU
#from datetime import datetime
import os.path
import signal
import math


PAPER="optimal-chunk-size"
ITEM = "consumer"

consumer = FlowConsumer(Id='test', name="/local/chunksize/dir/c.mp3", fout=None, monitor_out_dir=None, 
                              size_fix=1000, window_fix=20, rtt_fix=4.0)
consumer.start()

for chunkinfo in consumer.chunkInfos:
    pass



    
class Consumer(FlowConsumer):
    pass

