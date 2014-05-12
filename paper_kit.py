#! /usr/bin/env python
# -*- coding: utf-8 -*-

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
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT_DIR OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Written by: Xiaoke Jiang <shock.jiang@gmail.com>
#

import matplotlib#need to manually install py-matplotlib
matplotlib.use('Agg')
matplotlib.rcParams["font.size"] = 21
matplotlib.rcParams["xtick.labelsize"] = 18
matplotlib.rcParams["lines.linewidth"] = 3.0
matplotlib.rcParams["pdf.fonttype"] = 42
import matplotlib.pyplot as plt

from settings import log, OUTPUT_DIR
import settings

import sys
import platform
import time
import md5
import os, os.path
import signal, sys, time
import string
import smtplib
import inspect
import logging
import threading
import shlex, subprocess
import signal 
import random
from smtplib import SMTP
        
#************** Global Settings ****************************************

IS_MT = True #Multi Threads Run

IS_REFRESH = True
#IS_REFRESH = False

MAX_THREADN = 24

#OUT_DIR = OUTPUT_DIR
PAPER = "paperkit"
DEBUG = False
LOG_LEVEL = logging.DEBUG
LOG_LEVEL = logging.INFO

"""the platform of the system"""
HOSTOS = platform.system() 
if HOSTOS.startswith("Darwin"):#mac os x system, probably your local machine, debug mode
    DEBUG = True
    MAX_THREADN = 2 #for local notebook, we set a small threads number
    #LOG_LEVEL = logging.DEBUG #for local development, we need debug mode
    #OUTPUT_DIR += "-debug" #for local, output to a debug directory

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
MAX_THREADN = 1

#************** Global Settings ****************************************


'''log = logging.getLogger("paperKit") #root logger
format = logging.Formatter('%(levelname)8s:%(module)10s:%(funcName)20s:%(lineno)3d: %(message)s')
fh = logging.FileHandler("paperkit.log", mode="w")
fh.setFormatter(format)

sh = logging.StreamHandler() #console
sh.setFormatter(format)

log.addHandler(sh)
log.addHandler(fh)

log.setLevel(LOG_LEVEL)
'''
"""tag:
    >: a new task begins, this new task may contain serveral subtasks
    <: a task finishes, means that all the subtasks finishes
    +: underlying is called and begin
    -: underlying end
    !+: data cache reading begin
    !-: data cache reading end
    $: data cache writing
"""
    
class Manager:
    """ Super Class of all the manager class, name as an example, CaseTemplate, Dot, Line, Figure and Paper"""
    def __init__(self, Id, **kwargs): #kwargs["outType"]
        self.Id = Id
        self.isMT = IS_MT
        self.t0 = time.time() #the time instance is created

    
    def notify(self, way="email", **msg): #way="email"|"print"
        '''notify users about running result, currently there are two ways: email, print
        '''
        self.t1 = time.time()
        data = PAPER+" ends "+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.t1)))+ \
            " TotalN=" + str(CaseTemplate.TotalN) +" SuccessN="+str(CaseTemplate.SuccessN)+ \
            " ExistingN="+str(CaseTemplate.ExistingN) +" FailN="+str(CaseTemplate.FailN)
        data = msg.get("data", data)
        
        log.info(data)
        if way == "print":
            return
        
        TO = msg.get("to", ["shock.jiang@gmail.com"])
        FROM = "06jxk@163.com"
        SMTP_HOST = "smtp.163.com"
        user= "06jxk"
        passwords="jiangxiaoke"
        mailb = ["paper ends", data]
        mailh = ["From: "+FROM, "To: shock.jiang@gmail.com", "Subject: " +data]
        mailmsg = "\r\n\r\n".join(["\r\n".join(mailh), "\r\n".join(mailb)])
    
        send = SMTP(SMTP_HOST)
        send.login(user, passwords)
        rst = send.sendmail(FROM, TO, mailmsg)
        
        if rst != {}:
            self.log.warn("send mail error: "+str(rst))
        else:
            self.log.info("sending mail finished")
        send.close()
    
    
class DataCacheTemplate():
    """cache data to local file and if needed, read data from cache
        for CaseTemplate, we may get the data from cache, which is embeded in "run" mechanism; 
        however, for FigureTemplate, we just write the data to file if only needed
    """
    def __init__(self, Id, headers=None, datass=None, **kwargs): #headers = ["rowN", "latency", "hop"]
        self.Id = Id
        self.cacheout = os.path.join(OUTPUT_DIR, "cache")
        if not os.path.exists(self.cacheout):
            os.makedirs(self.cacheout)
            
        self.cacheout = os.path.join(self.cacheout, self.Id+"-datacache.txt")
            
        self.headers = headers
        self.datass = datass #[[], [], [], ...], ever sub[] is one column in the file, or belong to a same line in the figure
        if self.datass == None:
            self.datass = []
        
        self.is_refresh = kwargs.get("refresh", IS_REFRESH)

    def to_refresh(self):
        """ should re-run the task(most cases) or not (cache data is there and to_refresh=False)
            easy True, hard False
        """
        return self.is_refresh or (not os.path.exists(self.cacheout))
    
    def read(self):
        """read data from cache
        """
        log.info("!+ %s cache reading begins")
        fin = open(self.cacheout)
        if self.datass == None:
            self.datass = []
        if self.datass == []:
            pass
        else:
            assert isinstance(self.datass[0], list), "self.datass[0] is not a list"
            assert len(self.datass[0]) == 0, "self.datass[0] is not empty"
            
            self.datass = []
            
        for line in fin.readlines():
            line = line.strip()
            if line.startswith("#headers:"):
                cols = line[len("#headers:"):].strip().split("|")
                if self.headers == None:
                    for head in cols:
                        if header != "":
                            self.headers.append(col)
                            
            elif line.startswith("#command:") or line.startswith("#note:"):
                pass
            elif line != "":
                cols = line.split()
                li = [float(cols[i]) for i in range(len(cols))]
                self.datass.append(li)
                
        log.info("!- %s cache reading ends")     
       
    def write(self):
        """write data to cache
        layout: horizontal, every sublist will be placed in one row
    
        """
        if self.datass == None:
            log.critical("datass is None")
            return
            
        
        fout = open(self.cacheout, "w") #write the data to result file
        if self.headers != None:
            line = ""
            for header in self.headers:
                line += "|" + header
            line.strip()
            line = "#headers: " + line+"\n"
            fout.write(line)
        #line = "#command: " + case.cmd + "\n"
        #fout.write(line)
        #assert self.datass != None, "self.datass == None"
        assert isinstance(self.datass, list), "self.datass is not a list, %s" %(self.datass)
        #assert isinstance(self.datass[0], list), "self.datass[0] is not a list, %s" %(self.datass[0])
        
        for li in self.datass:
            for val in li:
                fout.write("%s\t" %(val))
            fout.write("\n")
            
        fout.flush()
        fout.close()
        log.info("$ " + self.Id+" cache writing")
       
                
class CaseTemplate(Manager, threading.Thread, DataCacheTemplate):
    """ run program/simulation case, trace file is printed to self.trace, console msg is printed to self.output
        and self.cacheout is stored the statstical information
        
        self.data
    """
    TotalN = 0
    LiveN = 0  #LiveN < MAX_THREADN
    SuccessN = 0
    ExistingN = 0
    FailN = 0  #TotalN = SuccessN + ExistingN + FailN
    
    def __init__(self, Id, **kwargs):
        threading.Thread.__init__(self)
        Manager.__init__(self, Id)
        DataCacheTemplate.__init__(self, Id, headers=["index", "value"], datass=None, kwargs=kwargs)
        
        self.setDaemon(True)
        self.result = None
        
        self.datas = []
   
    def start(self):
        CaseTemplate.LiveN += 1
        #log.debug("%s start" %(self.Id))
        threading.Thread.start(self)

    def run(self):
        """ run the case, after running, the statstical result is held in self.data as list
        """
        #CaseTemplate.LiveN += 1
        log.info("> " +self.Id+" begins TotalN/LiveN/SuccessN/ExistingN/FailN=%d/%d/%d/%d/%d" \
                      %(CaseTemplate.TotalN, CaseTemplate.LiveN, CaseTemplate.SuccessN, CaseTemplate.ExistingN, CaseTemplate.FailN))
        if not self.to_refresh():
            CaseTemplate.ExistingN += 1
            self.read()
            self.datas = self.datass[0]
            self.result = True
            pass
        else:    
            rst = self.underlying()
            if rst == True:
                CaseTemplate.SuccessN += 1
                self.result = True
                self.get_data()
                if not self.is_refresh:
                    self.write()
            else:
                log.error(self.Id+" return error" )
                if os.path.exists(self.cacheout):
                    os.remove(self.cacheout)
                CaseTemplate.FailN += 1
                self.result = False
                
        CaseTemplate.LiveN -= 1
        log.info("< " +self.Id+" ends TotalN/LiveN/SuccessN/ExistingN/FailN=%d/%d/%d/%d/%d" \
                      %(CaseTemplate.TotalN, CaseTemplate.LiveN, CaseTemplate.SuccessN, CaseTemplate.ExistingN, CaseTemplate.FailN))
    

    
    #waiting for override
    def underlying(self):
        log.info("+ %s begin" %(self.Id))
        log.info("- %s begin" %(self.Id))
        return True
    #waiting for override
    def get_data(self):
        """extract data from output of underlying and all the data should be stored in datass.
        """
        pass
    
class DotTemplate():        
    def __init__(self, x, y):
        self.x = x
        self.y = y  
        
class LineTemplate(Manager):
    def __init__(self, dots=None, xs=None, ys=None, plt={}, **kwargs):
        """plt: label(the key)
        """
        #for dot in dots:
        if dots != None:
            dotN = len(dots)
            self.xs = [dots[i].x for i in range(dotN)]
            self.ys = [dots[i].y for i in range(dotN)]
        else:
            dotN = len(xs)
            self.xs = xs
            self.ys = ys
            
        self.plt = plt

        
class FigureTemplate(Manager, DataCacheTemplate):
    """ information of Figure
        such as title, xlabel, ylabel, etc
    """
    def __init__(self, Id, lines=None, canvas={}, datass=None, **kwargs):
        Manager.__init__(self, Id, outType=".png")
        DataCacheTemplate.__init__(self, Id, headers=None, datass=None)
        if lines != None:
            self.lines = lines
        else:
            assert datass != None, "lines == None and datass == None"
            assert type(datass) == list, "datass is not list, datass=%s" %(datass)
            assert type(datass[0]) == list, "datass[0] is not the list, datass=%s" %(datass)
            self.lines = []
            
            xs = datass[0]
            for i in range(1, len(datass)):
                datas = datass[i]
                line = LineTempalte(dots=None, xs=xs, ys=datas)
                self.lines.append(line)
                
                
        self.canvas = canvas
        self.kwargs = kwargs
        self.pngout = os.path.join(settings.OUT_FIG_DIR, self.Id+".png")
        self.pdfout = os.path.join(settings.OUT_FIG_DIR, self.Id+".pdf")
        
    def line(self):
        log.debug(self.Id+" begin to draw ")
        plt.clf()
        
        cans = []
        for line in self.lines:
            log.debug("line.xs="+str(line.xs))
            log.debug("line.ys="+str(line.ys))
            log.debug("plt atts="+str(line.plt))
            can = plt.plot(line.xs, line.ys, line.plt.pop("style", "-"), **line.plt)
            #can = plt.scatter(x=line.xs, y=line.ys)
            cans.append(can)

        plt.grid(True)        
        plt.xlabel(self.canvas.pop("xlabel", " "))
        plt.ylabel(self.canvas.pop("ylabel", " "))    
        plt.xlim(xmax=self.canvas.pop("xmax", None))
        
        self.extend(plt)#extend line
        
        plt.legend(**self.canvas)
        #loc='lower/upper left'
        
        if HOSTOS.startswith("Darwin"):
            pass
        
        plt.savefig(self.pngout)
        plt.savefig(self.pdfout)
        log.debug(self.Id+" fig save to "+self.pngout)
        plt.close()
        
        log.info(self.Id+" ends")

    def scatter(self):
        log.debug(self.Id+" begin to draw ")
        plt.clf()
        
        cans = []
        for line in self.lines:
            log.debug("line.xs="+str(line.xs))
            log.debug("line.ys="+str(line.ys))
            log.debug("plt atts="+str(line.plt))
            #can = plt.plot(line.xs, line.ys, line.plt.pop("style", "-"), **line.plt)
            can = plt.scatter(x=line.xs, y=line.ys, s=self.kwargs.get("c", 1), **line.plt)
            cans.append(can)

        plt.grid(True)        
        plt.xlabel(self.canvas.pop("xlabel", "X"))
        plt.ylabel(self.canvas.pop("ylabel", "X"))    
        plt.xlim(xmax=self.canvas.pop("xmax", None))
        
        self.extend(plt)#extend line
        
        plt.legend(**self.canvas)
        #loc='lower/upper left'
        
        if HOSTOS.startswith("Darwin"):
            pass
        
        plt.savefig(self.pngout)
        plt.savefig(self.pdfout)
        log.debug(self.Id+" fig save to "+self.pngout)
        plt.close()
        
        log.info(self.Id+" ends")
    
    def extend(self, plt): #extend line
        log.warn("wait for override")
        pass
    
    def bar(self):
        log.debug(self.Id+" begin to draw ")
        plt.clf()
        
        self.bars = []
        Width = self.canvas.pop("width", 0.2)
        for i in range(len(self.lines)):
            line = self.lines[i]
        #for line in self.lines:
            print "line.xs=",line.xs
            print "line.ys=", line.ys
            xs = [x+i*Width for x in line.xs]
            bar = plt.bar(left=xs, height=line.ys, width=Width, bottom=0, align="center", **line.plt)
            self.bars.append(bar)
            
        #plt.legend( (p1[0], p2[0]), ('Men', 'Women') )
        
        plt.legend((self.bars[i][0] for i in range(len(self.lines))), (self.lines[i].plt["label"] for i in range(len(self.lines))))
        #for bar in self.bars:
        
        xs = [Width * len(self.lines)/2 + j for j in line.xs]
        plt.xticks(xs, line.xs)
                
        plt.grid(True)
        plt.xlabel(self.canvas.pop("xlabel", " "))
        plt.ylabel(self.canvas.pop("ylabel", " "))    
        plt.legend(**self.canvas)
        plt.title(self.canvas.pop("title", " "))
        #plt.xticklabels([]) 
        self.extend(plt)
        
        plt.legend(**self.canvas)
        plt.savefig(self.pngout)
        plt.savefig(self.pdfout)
        log.debug(self.Id+" fig save to "+self.pngout)
        plt.close()
        
        log.info(self.Id+" finishes")

class GodTemplate(Manager, threading.Thread):
    """ GodTemplate to control all the processes of the program, when to run cases, how to assign data and draw figs
    
    """
 
    IsError = False
    def start(self):
        threading.Thread.start(self)
        #signal.pause()
        
        
    def run(self):
        cases = self.cases

        log.info("> "+ self.Id + " run begins")
        CaseTemplate.TotalN = len(cases)
        keys = cases.keys()
        if len(keys)<= MAX_THREADN:
            for Id, case in cases.items():
                case.start()
                
            for Id, case in cases.items():
                if case.isAlive():
                    case.join()
        else:
            aliveThds = []
            for j in range(MAX_THREADN):
                key = keys[j]
                case = cases[key]
                aliveThds.append(case)
                case.start()
                
            next = MAX_THREADN
            
            while next < len(keys):
                endN = 0
                endThds = []
                for case in aliveThds: 
                    if case.isAlive() == False:
                        endN += 1
                        endThds.append(case)
                        if case.result == False:
                            God.IsError = True
                            break
                if GodTemplate.IsError:
                    break
                        
                for case in endThds:
                    aliveThds.remove(case)
                        
                for i in range(endN):
                    if next >= len(keys):
                        break
                    key = keys[next]
                    case = cases[key]
                    aliveThds.append(case)
                    case.start()
                    
                    next += 1
                
                #time.sleep(1)
                
            for case in aliveThds:
                if case.isAlive():
                    case.join()
                    #pass
                    #time.sleep(1)
                else:
                    if case.result == False:
                        GodTemplate.IsError = True
                        break
                    #aliveThds.remove(case)
                    #endThds.append(case)
            
        log.info("< "+ self.Id + " run ends with IsError="+str(GodTemplate.IsError) +\
                      " TotalN="+str(len(cases))+" SuccessN="+str(CaseTemplate.SuccessN)+ " ExsitingN="+str(CaseTemplate.ExistingN) +" FailN="+str(CaseTemplate.FailN))
        signal.alarm(1)
       
    def __init__(self, paper):
        """ GodTemplate will run all the cases needed
        """
        Manager.__init__(self, Id="GOD")
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.cases = {}
    
    def setup(self):
        """set up all the data needed, which should call run
        """
        pass
        
    def world(self, **kwargs):
        """create a world, which contains multiple days/figures
        """
        pass
    
    def monday(self, **kwargs):
        """create one thing/figure
        """
    def tuesday(self, **kwargs):
        """create another/figure
        """
