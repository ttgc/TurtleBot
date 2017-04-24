#!usr/bin/env/python3.4
#-*-coding:utf-8-*-
#AmperMusicAPI

import requests
import time
#import json
from threading import Thread

token_turtle = 'nytktIllKnIFa2ACEPHiAJ0jKfNhV7WI8ZIfUKp5E3ZN5lpJ5qu2Dejc67ycuL3w'

class AmperMusicAPI:
    def __init__(self,token):
        self.base_url = 'https://jimmy.ampermusic.com'
        self.header = {'Authorization': "Bearer "+token}

    def _get(self,complement):
        return requests.get(self.base_url+complement,headers=self.header)

    def _post(self,complement,data):
        return requests.post(self.base_url+complement,json=data,headers=self.header)

    def descriptors(self):
        return self._get('/v1/data/descriptors').json()

    def create(self,timeline,title="New Project",process=None):
        initial_req = self._post('/v1/projects',{'title':title,'timeline':timeline})
        data = initial_req.json()
        if process is not None: process.bind(data)
        ID = data["id"]
        while data["status"] == "waiting_create":
            req = self._get('/v1/projects/'+str(ID))
            data = req.json()
            time.sleep(0.1)
        if data["status"] == "failed_create":
            raise RuntimeError("Creation has failed")
        return data

    def get_url(self,data,wav=False):
        files = data["files"]
        if not wav:
            for i in files:
                if "mp3" in i["content_type"]:
                    return i
        else:
            for i in files:
                if "wav" in i["content_type"]:
                    return i

    def generate_timeline(self,theme,duration):
        endtype = {
            "time":duration,
            "end_type":"ending",
            "type":"ringout"
            }
        event1 = {
            "event":"region",
            "id":1,
            "time":0,
            "descriptor":theme,
            "end_type":endtype
            }
        event2 = {
            "event":"silence",
            "time":duration
            }
        timeline = {"events":[event1,event2]}
        return timeline

    def download(self,file,path="",wav=False):
        url = self.get_url(file,wav)
        data = self._get(url['download_url'].replace(self.base_url,""))
        extension = ".mp3"
        if wav: extension = ".wav"
        f = open(path+str(file['id'])+extension,'wb')
        f.write(data.content)
        f.close()
        return path+str(file['id'])+extension

class AmperGeneratorProcess(Thread):
    def __init__(self,theme,duration,title="New Project",path="",api=AmperMusicAPI(token_turtle),wav=False):
        Thread.__init__(self)
        self.api = api
        self.theme = theme
        self.duration = duration
        self.title = title
        self.wav = wav
        self.finished = False
        self.error = False
        self.project = None
        self.path = path
        self.process = AmperProcess(self.api)

    def run(self):
        timeline = self.api.generate_timeline(self.theme,self.duration)
        try: self.project = self.api.create(timeline,self.title,self.process)
        except:
            self.error = True
            self.finished = True
            return
        self.path = self.api.download(self.project,self.path,self.wav)
        self.finished = True

class AmperProcess:
    def __init__(self,api=AmperMusicAPI(token_turtle)):
        self.is_bind = False
        self.data = None
        self.progress = 0
        self.ID = None
        self.finished = False
        self.error = False
        self.base_url = 'https://jimmy.ampermusic.com'
        self.header = api.header

    def _get(self,complement):
        return requests.get(self.base_url+complement,headers=self.header)

    def bind(self,init_data):
        self.data = init_data
        self.progress = self.data['progress_percent']
        if self.data['status'] == 'created':
            self.progress = 100
            self.finished = True
        elif self.data['status'] == 'failed_create':
            self.progress = 0
            self.finished = False
            self.error = True
        if self.progress is None: self.progress = 0
        self.ID = self.data['id']
        self.is_bind = True

    def update(self):
        if not self.is_bind: return
        self.data = self._get('/v1/projects/'+str(self.ID)).json()
        self.bind(self.data)
