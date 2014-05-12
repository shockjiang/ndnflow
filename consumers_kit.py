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

import os
import os.path
import sys
import logging
import random
import signal
import socket

from ndn_flow import FlowConsumer, ChunkSizeEstimator

from paper_kit import PAPER, DEBUG
from paper_kit import CaseTemplate, DotTemplate, LineTemplate, FigureTemplate, GodTemplate, DataCacheTemplate



global PAPER
PAPER = "chunksize"

log = logging.getLogger("consumer2") #root logger, debug, info, warn, error, critical
 
#format = logging.Formatter('%(levelname)8s:%(funcName)23s:%(lineno)3d: %(message)s')
format = logging.Formatter('%(levelname)8s:%(module)10s:%(funcName)20s:%(lineno)3d: %(message)s')
fh = logging.FileHandler(PAPER+".log", mode="w")
fh.setFormatter(format)
 
sh = logging.StreamHandler() #console
sh.setFormatter(format)
 
log.addHandler(sh)
log.addHandler(fh)
 
log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)

class Case(CaseTemplate):
    def __init__(self, Id, **kwargs):
        CaseTemplate.__init__(self, Id, kwargs=kwargs)
        self.kwargs = kwargs
        self.csm = kwargs.pop("consumer")
        
    def get_data(self):
        OptimalChunkSizes, PacketLossRates, CongestionWindowSizes, Rto, TimeCost = self.csm.summary()
        
        self.datass += [OptimalChunkSizes, PacketLossRates, CongestionWindowSizes, Rto, TimeCost]
    
    def underlying(self):
        log.info("+ %s begin" %(self.Id))
        #log.debug("underlying call: argument: max=%s and min=%s" %(self.max, self.min))
        rst = self.csm.start()
        log.info(self.csm)
        log.info("- %s end, rst=%s" %(self.Id, rst))
        
        return True
    
class Dot(DotTemplate):
    def __init__(self, x, y):
        DotTemplate.__init__(self, x, y)

class Line(LineTemplate):
    def __init__(self, dots=None, xs=None, ys=None, plt={}, **kwargs):
        LineTemplate.__init__(self, dots=dots, xs=xs, ys=ys, plt=plt, kwargs=kwargs)
        
class Figure(FigureTemplate):
    def __init__(self, Id, lines, canvas={}, **kwargs):
        FigureTemplate.__init__(self, Id, lines, canvas=canvas, kwargs=kwargs)


#
#    h243(M) -> vt(M) -> super ->southeast
#    
class God(GodTemplate):
    def __init__(self, paper):
        GodTemplate.__init__(self, paper)
        
    def setup(self):
        #self, Id, name, fout, monitor_out_dir=
        self.producers = ["super", "vt", "southeast", "h243"]
        #self.producers = ["super", "vt"]
        self.producers = ["southeast"]
        #self.producers = ["local"]
        
        
        self.fnames = ["music.mp3"]
        self.fnames = ["img.jpg"]
        #self.fnames = ["c"]
        #self.fnames = ["d"]
        
        
        self.size_fixs = [None]
        self.window_fixs = [None]
        self.size_fixs = [None, 4096]
        #self.size_fixs = [4096]
        self.window_fixs = [None, 10]
        #self.window_fixs = [10]
        
        self.monitor_dir = "monitor"
        self.acquire_dir = "acquire"
        
        hostname = socket.gethostname().strip()
        producername = ""
        if hostname == "Shock-MBA.local":
            producername = "local"
        elif hostname == "ubuntuxyhu":
            producername = "southeast"
        elif hostname == "clarence-VirtualBox":
            producername = "vt"
        elif hostname == "tracy":
            producername = "uq"
        elif hostname == "R710":
            producername = "super"
        elif hostname == "shock-pc":
            producername = "h243"
        else:
            print "!!!! unknown hostname: %s" %(hostname)
        
        if producername in self.producers:
            self.producers.remove(producername)
        
        
        if not os.path.exists(self.acquire_dir):
            os.makedirs(self.acquire_dir)
            
        dic = {}
        
        for producer in self.producers:
            for fname in self.fnames:
                for size_fix in self.size_fixs:
                    for window_fix in self.window_fixs:
                        name = "/%s/chunksize/dir/%s" %(producer, fname)
                        Id = "%s-chunk%s-window%s-%s" %(producer, size_fix, window_fix, fname)
                        fout = open(os.path.join(self.acquire_dir, Id), "w")
                        csm = Consumer(Id=Id, name=name,fout=fout, monitor_out_dir=self.monitor_dir, \
                                            size_fix=size_fix, window_fix=window_fix)
                                                
                        case = Case(Id=Id, consumer=csm)
                        case.is_refresh = False
                        self.cases[Id] = case
                        
                
    def world(self, **kwargs):
        self.monday()
        self.tuesday()
    
    def monday(self, **kwargs): #draw  figure with all the case's data[0]
        lines = []
        lines2 = []
        lines3 = []
        lines4 = []
        
        for producer in self.producers:
            for fname in self.fnames:
                for size_fix in self.size_fixs:
                    for window_fix in self.window_fixs:
                        #label = "%s, %s, %s" %(fname, producer, size_fix)
                        label = "%s %s %s" %(producer, size_fix, window_fix)            
                        Id = "%s-chunk%s-window%s-%s" %(producer, size_fix, window_fix, fname)
                        case = self.cases[Id]
                        
                        #chunksize
                        ys = case.datass[0] #chunk size
                        ys2 = case.datass[1] #packet lossrate
                        ys3 = case.datass[2] #congestion window size
                        
                        plt = {"label":label}
                        xs = range(len(ys))
                        line = Line(Id=Id, xs=xs, ys=case.datass[0], plt=plt)
                        lines.append(line)
                        
                        xs = range(len(ys2))
                        line2 = Line(Id=Id, xs=xs, ys=ys2, plt=plt)
                        lines2.append(line2)
                        
                        xs = range(len(ys3))
                        line3 = Line(Id=Id, xs=xs, ys=ys3, plt=plt)
                        lines3.append(line3)
                        
                        ys = case.datass[3]
                        xs = range(len(ys))
                        line = Line(Id=Id, xs=xs, ys=ys, plt=plt)
                        lines4.append(line)
                        
                        
        canvas = {"loc":"upper right"}
        figure = Figure(Id="chunksize", lines=lines, canvas=canvas)
        figure.line()
        
        figure2 = Figure(Id="lossrate", lines=lines2, canvas=canvas)
        figure2.line()
        
        
        figure3 = Figure(Id="windowsize", lines=lines3, canvas=canvas)
        figure3.line()
        
        
        figure4 = Figure(Id="rto", lines=lines4, canvas=canvas)
        figure4.line()
        
    def tuesday(self, **kwargs):
        """two lines: min =[50, 90]
            x: max=range(100,200,20)
            y: case.data[1]
        """
        lines = []
        lines2 = []
        lines3 = []
        lines4 = []
        dots = []
        x = 0
        for producer in self.producers:
            for fname in self.fnames:
                for size_fix in self.size_fixs:
                    for window_fix in self.window_fixs:
                        #label = "%s, %s, %s" %(fname, producer, size_fix)
                        Id = "%s-chunk%s-window%s-%s" %(producer, size_fix, window_fix, fname)
                        case = self.cases[Id]
                        
                        #chunksize
                        y = case.datass[4][0]
                        
                        dot = Dot(x=x, y=y)
                        dots.append(dot)
                        x += 1
                        
            label = "%s" %(producer)            
        
        plt = {"label":label}
        line = Line(dots=dots, plt=plt)
        lines.append(line)
        
        figure = Figure(Id="timecost", lines=lines)
        figure.bar()
        
                        

def signal_handler(signum, frame):
    if signum == signal.SIGINT:
        log.critical("--------------YOU PRESS CTRL+C, PROGRAM QUITE!--------------")
        sys.exit(0)
    elif signum == signal.SIGALRM:
        log.info("all the cases end")

signal.signal(signal.SIGTERM,signal_handler)
signal.signal(signal.SIGALRM, signal_handler)


def main():
    god = God(paper=PAPER)
    
    god.setup()
    god.start()
    signal.pause()
    god.world()
    

class Consumer(FlowConsumer):
    def __init__(self, Id, name, fout, monitor_out_dir="./", enable_monitor=True, size_fix=None, window_fix=None, rtt_fix=None):
        FlowConsumer.__init__(self, Id=Id, name=name, fout=fout, monitor_out_dir=monitor_out_dir, 
                              size_fix=size_fix, window_fix=window_fix, rtt_fix=None)
    
    #override FlowConsumer
    def start(self):
        log.info("start consumer: %s" %(self.Id))
        rst = FlowConsumer.start(self)
        return rst

    
    
def testLocal():
    fout = open("c", "w")
    producers = ["local"]
    for producer in producers:
        temp = 0
        while temp <1:
            temp += 1
            #for ID in ["c"]:
            for ID in ["img.jpg"]:
                Id=producer+"-chunksize-congestionwindow"
                csm = Consumer(Id=Id, monitor_out_dir="output", size_fix=4096, name="/"+producer+"/chunksize/dir/"+ID, fout=fout)
                #csm.mydata.next_byte = 2188366
                csm.start()
                
    
    
def testFlowConsumer():
    fout = open("c", "w")
    producers = ["vt"]
    for producer in producers:
        temp = 0
        while temp <1:
            temp += 1
            #for ID in ["c"]:
            for ID in ["img.jpg"]:
                Id=producer+"-chunksize-congestionwindow"
                csm = Consumer(Id=Id, monitor_out_dir="output", size_fix=4096, name="/"+producer+"/chunksize/dir/"+ID, fout=fout)
                #csm.mydata.next_byte = 2188366
                csm.start()
                
            #csm.summary()
            
def testEstimator():
    est = ChunkSizeEstimator(packet_max_data_size=1472)
    for i in range(30):
        est.lostN = i
        est.receivedN = 200 - i
        print "lossrate=%s, optimal data size=%s" %(float(i)/200, est.get_optimal_data_size())
        
    
if __name__=="__main__":
    #signal.signal(signal.SIGINT, signal_handler)
    #testEstimator()
    #testFlowConsumer()
    if DEBUG:
        #main()
        testLocal()
        #testFlowConsumer()
    else:
        main()

    
    #testFlowConsumer()
