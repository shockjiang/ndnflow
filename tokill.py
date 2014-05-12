#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import signal
import argparse


def go(keyword, group, list, **kwargs):
    lines =  os.popen("ps xa|grep %s" %(keyword)).readlines()
    
    keywords = ["./%s" %(keyword), "python %s"%(keyword)]
    if group:
        keywords.append("./group_%s"%(keyword))
        keywords.append("python group_%s" %(keyword))
    print "the keywords used to search: %s" %(keywords)
    
    if list:
        print "The following apps are picked according to the keywords:"
    #print lines
    for line in lines:
        line = line.strip()
        fields = line.split()
        pid = int(fields[0])
        #process = fields[4].lower()
        process = line.lower()
        #print process
        
        if process.find("grep %s" %(keyword)) >=0:
            #print "DO NOT print %s" %(line)
            continue
        if group and process.find("grep group_%s" %(keyword)) >=0:
            #print "DO NOT print %s" %(line)
            continue
        
        
        for kw in keywords:
            if process.find("%s" %(kw)) >=0:
                if list:
                    print line
                else:
                    print "TO kill: %s" %(line)
                    os.kill(pid, signal.SIGHUP)
                break
            else:
                #print "%s pass keyword: %s" %(process, kw)
                pass
    
    print "The app Finishes"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Configure the arguments of this program')
    parser.add_argument("-k", "--keyword", help="The keyword that will use to identify app", default="consumer")
    parser.add_argument("-g", "--group", help="Kill Group with with keyword: group_<Keyword>", dest="group", action='store_true')
    parser.add_argument("-l", "--list", help="List the programs only without kill them", dest="list", action="store_true")
    #parser.add_argument("-s", "--fixsize", help="the chunk size fixed to the program, default is 1000", default=1000)
    #parser.add_argument("-w", "--windowsize", help="the window size fixed to send packet, default is 1", default=20)
    args = parser.parse_args()
    
    go(keyword=args.keyword, group=args.group, list=args.list)
        
            