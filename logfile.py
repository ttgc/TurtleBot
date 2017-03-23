#!usr/bin/env python3.4
#-*-coding:utf-8-*-
#logfile manager

import os,time

def singleton(classe_definie):
    instances = {} # Dictionnaire de nos instances singletons
    def get_instance():
        if classe_definie not in instances:
            # On crée notre premier objet de classe_definie
            instances[classe_definie] = classe_definie()
        return instances[classe_definie]
    return get_instance

@singleton
class LogSystem:
    def __init__(self):
        self.limit = -1 #limit = -1 = no limit
        self.directory = ""

    def clean(self):
        if len(os.listdir(self.directory)) >= self.limit:
            ls = os.listdir(self.directory)
            fdel = ls[0]
            for i in os.listdir(self.directory):
                if os.stat(self.directory+"/"+i).st_ctime < os.stat(self.directory+"/"+fdel).st_ctime:
                    fdel = i
            os.remove(self.directory+"/"+fdel)

class Logfile:
    def __init__(self,name,system):
        self.name = name
        self.sys = system
        self.file = None

    def start(self):
        self.sys.clean()
        self.file = open(self.sys.directory+"/"+self.name+".log",'w+')
        self.append("OPENING","Starting using the file log")

    def restart(self):
        self.file = open(self.sys.directory+"/"+self.name+".log",'a')

    def append(self,title,msg):
        tps = time.localtime()
        self.file.write("["+str(tps.tm_mday)+"/"+str(tps.tm_mon)+"/"+str(tps.tm_year)+"_"+str(tps.tm_hour)+":"+str(tps.tm_min)+":"+str(tps.tm_sec)+"]["+title+"] "+msg+"\n")
        return tps

    def stop(self):
        self.file.close()
