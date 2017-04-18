#!usr/bin/env python3.4
#-*-coding:utf-8-*-
#MojangAPI - Turtle Edition

import urllib.request as urllib2
import json
import base64

def singleton(classe_definie):
    instances = {} # Dictionnaire de nos instances singletons
    def get_instance():
        if classe_definie not in instances:
            # On crée notre premier objet de classe_definie
            instances[classe_definie] = classe_definie()
        return instances[classe_definie]
    return get_instance

@singleton
class MojangAPI:

    def _get_json(self, url):
        req = urllib2.Request(
            url=url, headers={'Content-Type': 'application/json'})
        response = json.loads(urllib2.urlopen(req).read().decode())

        return response

    def _post_json(self, url, data):
        req = urllib2.Request(
            url=url, headers={'Content-Type': 'application/json'}, data=json.dumps(data).encode())
        response = json.loads(urllib2.urlopen(req).read().decode())

        return response

    def service_statuses(self, service=None):
        url = 'http://status.mojang.com/check'

        if service is not None:
            url = url + '?service=' + service

        statuses = self._get_json(url)
        return statuses

##    def mojang_news(self):
##        url = 'http://status.mojang.com/news'
##
##        return self._get_json(url)

    def get_uuid(self, username):
        url = 'https://api.mojang.com/profiles/minecraft'#/page/1'

        data = [#{
            username#'name': username,
            #'agent': 'minecraft'
        ]#}

        uuid = self._post_json(url, data)

        if len(uuid) is not 1:
            return None

        return uuid[0]['id']#['profiles'][0]

    def get_profile(self,uuid):
        url = 'https://sessionserver.mojang.com/session/minecraft/profile/'+uuid#+'?unsigned=false'
        profil = self._get_json(url)
        profil['properties'][0]['value'] = base64.b64decode(profil['properties'][0]['value']).decode()
        return profil

    def get_skin(self,profil):
        item = profil['properties'][0]['value']
        start,end = item.find("SKIN"),item.find('"}')
        item = item[start:end]
        item = item[item.find('"url":'):]
        return item.replace('"url":"',"")
