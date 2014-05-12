#/usr/bin/env python
'''
@author Xiaoke Jiang <shock.jiang@gmail.com>
This script aims to get the chunk loss/fetch distribution

@version: 0.1, 7 May, 2014

'''

#kind=loss, time=0:00:00.139838, index=331, beginT=2014-05-07 17:23:26.772008, begin_byte=331000, endT=None, end_byte=331999, packetN=1.0, retxN=1, data_size=None, chunk_size=0, status=1
#import paper_kit

import sys
import os

PAR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not PAR_DIR in sys.path:
    sys.path.append(PAR_DIR)
    print "add PAR_DIR"
else:
    print "PAR_DIR is already in path"
    
#print sys.path
from paper_kit import FigureTemplate, LineTemplate
from settings import ROOT_DIR, log
import settings

class Stat(object):
    def __init__(self, fpath=os.path.join(settings.OUT_DATA_DIR, "upcall_events-test.log"), **kwargs):
        
        self.fpath = fpath
        self.datas = []
        
    def stat(self):
        f = open(self.fpath)
        
        lastkind = "none"
        count = 0
        
        for line in f.readlines():
            parts = line.split(",")
            kind = parts[0].split("=")[1]
            index = parts[2].split("=")[1]
            
            if kind == lastkind:
                count += 1
            else:
                count = 1
                if kind == "loss":
                    count = -1 * count
                
                self.datas.append(count)
                

                #print "kind=%s, count=%s" %(kind, count)
                if kind != "loss" and kind != "fetch":
                    print "!!!!!!!!kind = %s" %(kind)
                
                count = 0
        
        log.info("datas contains %d elements" %(len(self.datas)))
        
    def draw(self):
        xs = range(len(self.datas))
        line = LineTemplate(Id="line-test", xs=xs, ys=self.datas, plt={"label":"1: fetch, -1:loss"})
        fig = FigureTemplate(Id="event_log-test", lines=[line])
        fig.scatter()

if __name__ == "__main__":
    stat = Stat()
    stat.stat()
    stat.draw()
    
            
        