#!/usr/bin/env python
# Copyright (c) 2013, Tsinghua University, P.R.China 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Tsinghua University nor
#       the names of its contributors may be used to endorse or promote
#       products derived from this software without specific prior written
#       permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL REGENTS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Written by: Xiaoke Jiang <shock.jiang@gmail.com>
#

from ndn_flow import FlowProducer

import os
import os.path
import sys
import signal
import socket

def main():
    #ip = get_ip_address("en0")
    
    hostname = socket.gethostname().strip()
    producername = ""
    if hostname == "Shock-MBA.local" or hostname == "shockair.local":
        producername = "local"
    elif hostname == "shock-vb":
        producername = "guoao"
    elif hostname == "j06":
        producername = "j06"
    elif hostname == "zhaogeng-OptiPlex-780":
        producername = "l07"
    elif hostname == "ndngateway2":
        producername = "tbed"
    elif hostname == "R710":   
        producername = "super"
    elif hostname == "user-virtual-machine":
        producername = "telcom"
    elif hostname == "shock-pc":
        producername = "h243"
    elif hostname == "ndn":
        producername = "h242"
    elif hostname == "ubuntuxyhu":
        producername = "seu"
    elif hostname == "clarence-VirtualBox": #node is down
        producername = "vt"
    else:
        producername = "local"
        print "!!!! unknown hostname: %s. We just use the producer prefix: local" %(hostname)
        #return
    
    #producer = Producer(name="/%s/chunksize/dir/x" %(producername), path="./dir/c", is_dir=False)
    #producer.start()
    media_path = os.path.dirname(__file__)
    media_path = os.path.join(media_path, "dir/")
    producer = Producer(name="/%s/chunksize/dir" %(producername), path=media_path, is_dir=True)
    producer.start()
    
class Producer(FlowProducer):
    def __init__(self, name, path, is_dir=True):
        FlowProducer.__init__(self, name=name, path=path, is_dir=is_dir)
    
    def start(self):
        print "start producer"
        FlowProducer.start(self)
        
def signal_handler(signal, frame):
        print "--------------YOU PRESS CTRL+C, PROGRAM QUITE!--------------"
        sys.exit(0)

if __name__=="__main__":
    signal.signal(signal.SIGINT, signal_handler)
    #testEstimator()
    #testFlowConsumer()
    #testFlowConsumer()
    main()
    #testFlowConsumer()
