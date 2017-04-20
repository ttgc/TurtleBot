#!usr/bin/env python3.4
#-*-coding:utf-8-*-

import discord
import asyncio
import logging
import os
import time
import urllib.request as urllibr
import urllib.parse as urllibp
import re
from logfile import *
from INIfiles import *
from random import *
from mojangapi import *
from VocalUtilities import *

global prefix,logf,config,lang,guild,report,pray,statut,vocalsys
prefix = "/"
statut = discord.Game(name="/help")
vocalsys = VocalSystem()

logger = logging.getLogger('discord')
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler(filename='Logs/discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

def convert_str_into_dic(string):
    if string == "{}": return {}
    string = string.replace("{","")
    string = string.replace("}","")
    string = string.replace("'","")
    #string = string.replace(" ","")
    ls = string.split(", ")
    dic = {}
    for i in range(len(ls)):
        temp = ls[i].split(": ")
        dic[temp[0]] = temp[1]
    return dic

def convert_str_into_ls_spe(string):
    if string == "{}": return []
    string = string.replace("{","")
    string = string.replace("}","")
    string = string.replace("'","")
    ls = string.split(", ")
    return ls

def convert_ls_into_str_spe(ls):
    string = str(ls)
    string = string.replace("[","{")
    string = string.replace("]","}")
    return string

def find_max(ls):
    count = {}
    for i in ls:
        if not i in count: count[i] = 0
        count[i] += 1
    result = None
    for i in count.keys():
        if result == None:
            result = i
            continue
        if count[i] >= count[result]:
            result = i
    return result

def save_data():
    global prefix,config,strikes,guild,guildlink,report,pray
    config.key_add("main","prefix",prefix)
    config.key_add("main","lang",str(lang))
    config.key_add("main","strikes",str(strikes))
    config.key_add("main","guild",str(guild))
    config.key_add("main","guild_link",str(guildlink))
    config.key_add("main","report",convert_ls_into_str_spe(report))
    for i in pray.keys():
        config.key_add("gods",i,convert_ls_into_str_spe(pray[i]))
    config.save("config")

client = discord.Client()
vocalsys.bot = client

@client.event
@asyncio.coroutine
def on_ready():
    global logf
    yield from client.change_presence(game=discord.Game(name="/help"))
    logf.restart()
    logf.append("Initializing","Bot is now ready")
    logf.stop()
##    f = open("turtle.png","rb")
##    yield from client.edit_profile(avatar=f.read())
##    f.close()

@client.event
@asyncio.coroutine
def on_message(message):
    global prefix,logf,lang,strikes,guild,guildlink,report,pray,statut,vocalsys
    #check bot
    if message.author.bot: return
    #check roles
    logf.restart()
    admin = modo = restricted = False
    serv = True
    if not message.server == None:
        hierarchy = message.server.role_hierarchy
        if message.author.top_role == hierarchy[0]:
            admin = True
            modo = True
        elif message.author.top_role == hierarchy[1]:
            modo = True
    else:
        hierarchy = None
        serv = False
    #check restrictions
    try:
        if strikes[str(message.author.id)] >= 3: restricted = True
    except KeyError: pass
    #check langage
    fr = False
    if lang[str(message.author.id)] == "FR": fr = True
    #general commands
    if message.content.startswith(prefix+'yay') and (not restricted):
        f = open("YAY.png","rb")
        yield from client.send_file(message.channel,f,content="YAY !")
        f.close()
    if message.content.startswith(prefix+'tell') and serv and (not restricted):
        msg = (message.content).replace(prefix+'tell ',"")
        print(str(message.author)+" : "+msg)
        logf.append("/tell",str(message.author)+" : "+msg)
        yield from client.delete_message(message)
        yield from client.send_message(message.channel,msg)
    if message.content.startswith(prefix+'setlang'):
        msg = (message.content).replace(prefix+'setlang ',"")
        if msg == "fr" or msg == "FR" or msg == "Fr":
            lang[str(message.author.id)] = "FR"
            yield from client.send_message(message.channel,"Le changement de langue vers FR a été pris en compte "+message.author.mention)
        elif msg == "en" or msg == "EN" or msg == "En":
            lang[str(message.author.id)] = "EN"
            yield from client.send_message(message.channel,"Switching language into EN has been performed succesful "+message.author.mention)
        else:
            if fr: yield from client.send_message(message.channel,"Langue inexistante")
            else: yield from client.send_message(message.channel,"Unexisting language")
    if message.content.startswith(prefix+'setprefix') and admin and serv:
        prefix = (message.content).replace(prefix+'setprefix ',"")
        logf.append("/setprefix","Changing command prefix into : "+prefix)
        yield from client.send_message(message.channel,"Changing command prefix into : "+prefix)
    if message.content.startswith(prefix+'profil') and serv:
        if len(message.mentions) != 0:
            profil = message.mentions[0]
        else:
            profil = message.author
        try: strik = strikes[str(profil.id)]
        except KeyError: strik = 0
        if not serv: rol = "Undefined"
        else:
            if profil.bot: rol = "Bot"
            elif profil.top_role == hierarchy[0]: rol = "Admin"
            elif profil.top_role == hierarchy[1]: rol = "Modo"
            elif profil.top_role == hierarchy[2]: rol = "Dev"
            elif profil.top_role == hierarchy[3]: rol = "VIP"
            else: rol = "Player"
        try: gd = guild[str(profil.id)]
        except KeyError: gd = "Indep"
        if profil.bot: gd = "None"
        embd = discord.Embed(title=profil.name,description="User Profile",colour=profil.top_role.color)
        embd.set_footer(text="Skycraft Discord Profile",icon_url="http://skycraft.tech/wp-content/uploads/2016/08/cropped-Computercraft.png")
        embd.set_image(url=profil.avatar_url)
        embd.set_thumbnail(url="http://skycraft.tech/wp-content/uploads/2016/08/Skycraft.png")
        embd.set_author(name=profil.name,icon_url=profil.avatar_url)
        embd.add_field(name="Language :",value=lang[str(profil.id)],inline=True)
        embd.add_field(name="Rank :",value=rol,inline=True)
        embd.add_field(name="Strike :",value=str(strik),inline=True)
        embd.add_field(name="Faction :",value=gd,inline=True)
        if not str(profil.id) in pray:
            mpray = "none"
            lpray = "none"
        else:
            mpray = find_max(pray[str(profil.id)])
            lpray = pray[str(profil.id)][-1]
        embd.add_field(name="Most Prayed God :",value=mpray,inline=True)
        embd.add_field(name="Latest Prayed God :",value=lpray,inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if message.content.startswith(prefix+'website'):
        embd = discord.Embed(title="Skycraft",description="Moded Role Play Minecraft Server using 1.7.10",colour=discord.Color(int("7289da",16)),url="http://skycraft.tech")
        embd.set_footer(text="Skycraft Server",icon_url="http://skycraft.tech/wp-content/uploads/2016/08/cropped-Computercraft.png")
        embd.set_thumbnail(url="http://skycraft.tech/wp-content/uploads/2016/08/Skycraft.png")
        embd.set_author(name=message.author.name,url="http://skycraft.tech",icon_url=message.author.avatar_url)
        embd.add_field(name="Mods :",value="Aether, Computercraft, Thaumcraft, IndustrialCraft2, BuildCraft, Archimed's ships +",inline=False)
        embd.add_field(name="IP for joining :",value="Genius.playat.ch",inline=False)
        embd.add_field(name="Minecraft Version :",value="1.7.10",inline=True)
        yield from client.send_message(message.channel,embed=embd)
    if message.content.startswith(prefix+'report') and serv and (not restricted):
        if len(message.mentions) != 0:
            for i in message.mentions:
                report.append(i.name)
                yield from client.send_message(message.channel,i.mention+" reported by "+message.author.mention)
    if message.content.startswith(prefix+'gods'):
        if message.content.startswith(prefix+'gods list'):
            f = open("gods.txt","r")
            ls = f.readlines()
            f.close()
            for i in range(len(ls)):
                ls[i] = ls[i].replace("\n","")
            if fr: f = open("godsatt_FR.txt","r")
            else: f = open("godsatt_EN.txt","r")
            att = f.readlines()
            f.close()
            for i in range(len(att)):
                att[i] = att[i].replace("\n","")
            if fr: embd = discord.Embed(title="Dieux",description="Il y a actuellement 18 Dieux dont l'existence est prouvée",colour=discord.Color(int("ffffff",16)))
            else: embd = discord.Embed(title="Gods",description="There are currently 18 gods recorded",colour=discord.Color(int("ffffff",16)))
            embd.set_footer(text="Skycraft Gods List")
            for i in range(len(ls)):
                embd.add_field(name=ls[i],value=att[i],inline=True)
            yield from client.send_message(message.channel,embed=embd)
        if message.content.startswith(prefix+'gods pray'):
            f = open("gods.txt","r")
            ls = f.readlines()
            f.close()
            for i in range(len(ls)):
                ls[i] = ls[i].replace("\n","")
            god = (message.content).replace(prefix+'gods pray ',"")
            if god in ls:
                if not str(message.author.id) in pray: pray[str(message.author.id)] = []
                pray[str(message.author.id)].append(god)
                yield from client.send_message(message.channel,message.author.mention+" prayed "+god)
    if message.content.startswith(prefix+'quote') and serv and (not restricted):
        tags = message.content.replace(prefix+'quote ',"").split(" ")
        if len(tags) == 0: return
        elif len(tags) > 1:
            while "" in tags:
                tags.remove("")
            if len(tags) > 2: del(tags[2:])
            #if tags[1] == "": del(tags[1])
        else:
            tags.append(message.channel.id)
        search_chan = client.get_channel(tags[1])
        if search_chan is None:
            yield from client.send_message(chan,"Channel not found "+auth.mention)
            return
        try:
            result = yield from client.get_message(search_chan,tags[0])
        except discord.NotFound:
            result = None
##        tags = message.content.replace(prefix+'quote ',"").split(" ")
##        lsresult = []
        chan = message.channel
        auth = message.author
        content = message.content
        yield from client.delete_message(message)
##        cache = client.messages
##        cache = cache.reverse()
##        for i in tags:
##            search = lambda m: i in m.content
##            temp = discord.utils.find(search,client.messages)
##            if temp is not None and temp.content is not content: lsresult.append(temp)
##        result = find_max(lsresult)
        if result is None:
            yield from client.send_message(chan,"No message found "+auth.mention)
            return
        embd = discord.Embed(title="Quotation from "+result.author.name,description=result.content,colour=discord.Color(randint(0,16777215)))
        embd.set_footer(text=(str(result.timestamp).split("."))[0])
        embd.set_author(name=result.author.name,icon_url=result.author.avatar_url)
        yield from client.send_message(chan,auth.mention+" :",embed=embd)
    #moderation commands
    if message.content.startswith(prefix+'strike') and modo and serv and (not restricted):
        if len(message.mentions) != 0:
            for i in message.mentions:
                if modo and (not admin) and (i.top_role == hierarchy[0] or i.top_role == hierarchy[1]) and message.author != message.server.owner:
                    yield from client.send_message(message.channel,i.mention+" Can not be striked by you due to his higher or equal rank")
                    continue
                if admin and i.top_role == hierarchy[0] and message.author != message.server.owner:
                    yield from client.send_message(message.channel,i.mention+" Can not be striked by you due to his higher or equal rank")
                    continue
                try: strikes[str(i.id)] += 1
                except KeyError:
                    strikes[str(i.id)] = 1
                if lang[str(i.id)] == "FR":
                    embd = discord.Embed(title="Strike",description="Vous avez reçu de la part de l'équipe un avertissement !\nVous avez reçu cet avertissement pour ne pas avoir respecté les regles d'utilisation du serveur discord visible en utilisant la commande '/rules'\nEn cas de récidive des sanctions seront automatiquement appliquées pouvant aller jusqu'au kick ou ban def suivant le tableau suivant :\n1 Strike = rien\n2 Strikes = rien\n3 Strikes = restriction\n4 Strikes = kick\n5 Strikes = Perma ban\n\nVeuillez respecter les règles du serveur pour éviter tout nouvel avertissement\nMerci de votre compréhension",colour=discord.Color(int("ff0000",16)))
                    embd.add_field(name="Nombre de strike reçus :",value=str(strikes[str(i.id)]),inline=False)
                    embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
                    embd.set_thumbnail(url="http://skycraft.tech/wp-content/uploads/2016/08/Skycraft.png")
                    yield from client.send_message(message.channel,i.mention+"\n",embed=embd)
                else:
                    embd = discord.Embed(title="Strike",description="You have got a strike from the staff !\nYou have got it for unrespect of the rules of the discord server that you can claim with the '/rules' command\nIn case of a new strike, you would probably get an automatic penalization including kick or perma ban following this table :\n1 Strike = Nothing\n2 Strikes = Nothing\n3 Strikes = Restrictions\n4 Strikes = kick\n5 Strikes = Perma ban\n\nPlease respect the rules of the server to avoid a new strike\nThanks to your understanding",colour=discord.Color(int("ff0000",16)))
                    embd.add_field(name="Strikes received :",value=str(strikes[str(i.id)]),inline=False)
                    embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
                    embd.set_thumbnail(url="http://skycraft.tech/wp-content/uploads/2016/08/Skycraft.png")
                    yield from client.send_message(message.channel,i.mention+"\n",embed=embd)
                if strikes[str(i.id)] == 4: yield from client.kick(i)
                if strikes[str(i.id)] == 5:
                    yield from client.send_message(message.channel,"```\n"+i.mention+" Has been perma-banned due to a high strikes number")
                    yield from client.ban(i)
                    del(strikes[str(i.id)])
    if message.content.startswith(prefix+'unstrike') and modo and serv and (not restricted):
        if len(message.mentions) != 0:
            for i in message.mentions:
                if modo and (not admin) and (i.top_role == hierarchy[0] or i.top_role == hierarchy[1]) and message.author != message.server.owner:
                    yield from client.send_message(message.channel,i.mention+" Can not be unstriked by you due to his higher or equal rank")
                    continue
                if admin and i.top_role == hierarchy[0] and message.author != message.server.owner:
                    yield from client.send_message(message.channel,i.mention+" Can not be unstriked by you due to his higher or equal rank")
                    continue
                try: strikes[str(i.id)] -= 1
                except KeyError: return
                if strikes[str(i.id)] == 0: del(strikes[str(i.id)])
                yield from client.send_message(message.channel,i.mention+" unstriked successful")
    if message.content.startswith(prefix+'faction') and serv:
        if message.content.startswith(prefix+'faction create') and modo:
            name = (message.content).replace(prefix+'faction create ',"")
            guildlink[name] = "None"
            yield from client.send_message(message.channel,"Faction "+name+" has been created succesful")
        if message.content.startswith(prefix+'faction delete') and modo and (not restricted):
            name = (message.content).replace(prefix+'faction delete ',"")
            try: del(guildlink[name])
            except KeyError: return
            yield from client.send_message(message.channel,"Faction "+name+" has been deleted succesful")
        if message.content.startswith(prefix+'faction linkto') and modo and (not restricted):
            if len(message.role_mentions) == 1:
                name = (message.content).replace(prefix+'faction linkto ',"")
                name = name.replace(message.role_mentions[0].mention+" ","")
                if name in guildlink:
                    guildlink[name] = str(message.role_mentions[0].id)
                    yield from client.send_message(message.channel,"Faction "+name+" has been linked to the role "+message.role_mentions[0].mention)
        if message.content.startswith(prefix+'faction add'):
            if modo and len(message.mentions) != 0:
                name = (message.content).replace(prefix+'faction add ',"")
                for i in message.mentions:
                    name = name.replace(" "+i.mention,"")
                if name == "" and (hierarchy[5] in message.author.roles): name = guild[str(message.author.id)]
                if not name in guildlink: return
                for i in message.mentions:
                    guild[str(i.id)] = name
                    yield from client.send_message(message.channel,i.mention+" has joined faction "+name)
                    if guildlink[name] != "None":
                        yield from client.add_roles(i,discord.utils.get(message.server.roles,id=guildlink[name]))
            elif (hierarchy[5] in message.author.roles) and len(message.mentions) != 0:
                for i in message.mentions:
                    guild[str(i.id)] = guild[str(message.author.id)]
                    yield from client.send_message(message.channel,i.mention+" has joined faction "+guild[str(message.author.id)])
                    if guildlink[name] != "None":
                        yield from client.add_roles(i,discord.utils.get(message.server.roles,id=guildlink[name]))
        if message.content.startswith(prefix+'faction remove'):
            if modo and len(message.mentions) != 0:
                name = (message.content).replace(prefix+'faction remove ',"")
                for i in message.mentions:
                    name = name.replace(" "+i.mention,"")
                if name == "" and (hierarchy[5] in message.author.roles): name = guild[str(message.author.id)]
                if not name in guildlink: return
                for i in message.mentions:
                    if message.author == i:
                        yield from client.send_message(message.channel,i.mention+" You canot remove yourself from faction. Use '/faction leave' to leave your faction")
                        continue
                    if guild[str(i.id)] == name:
                        guild[str(i.id)] = "None"
                        yield from client.send_message(message.channel,i.mention+" has been removed from faction "+name)
                        if guildlink[name] != "None":
                            yield from client.remove_roles(i,discord.utils.get(message.server.roles,id=guildlink[name]))
                        if hierarchy[5] in i.roles:
                            yield from client.remove_roles(i,hierarchy[5])
                    else:
                        yield from client.send_message(message.channel,i.mention+" doesn't belong to the faction "+name)
            elif (hierarchy[5] in message.author.roles) and len(message.mentions) != 0:
                for i in message.mentions:
                    if message.author == i:
                        yield from client.send_message(message.channel,i.mention+" You canot remove yourself from faction. Use '/faction leave' to leave your faction")
                        continue
                    if guild[str(i.id)] == guild[str(message.author.id)]:
                        name = guild[str(i.id)]
                        guild[str(i.id)] == "None"
                        yield from client.send_message(message.channel,i.mention+" has been removed from faction "+name)
                        if guildlink[name] != "None":
                            yield from client.remove_roles(i,discord.utils.get(message.server.roles,id=guildlink[name]))
                    else:
                        yield from client.send_message(message.channel,i.mention+" doesn't belong to the faction "+name)
        if message.content.startswith(prefix+'faction leave'):
            if guild[str(message.author.id)] != "None":
                name = guild[str(message.author.id)]
                guild[str(message.author.id)] = "None"
                yield from client.send_message(message.channel,message.author.mention+" left the faction "+name)
                if guildlink[name] != "None":
                    yield from client.remove_roles(message.author,discord.utils.get(message.server.roles,id=guildlink[name]))
                if hierachy[5] in message.author.roles:
                    yield from client.remove_roles(message.author,hierarchy[5])
            else:
                yield from client.send_message(message.channel,message.author.mention+" You doesn't belong to any faction")
    if message.content.startswith(prefix+'showreport') and modo:
        yield from client.send_message(message.channel,str(report))
    if message.content.startswith(prefix+'cleanreport') and modo:
        nbr = (message.content).replace(prefix+'cleanreport',"")
        try: nbr = int(nbr)
        except ValueError: nbr = -1
        if nbr == -1:
            report = []
            yield from client.send_message(message.channel,"Reports cleaned")
        else:
            for i in range(nbr):
                try: del(report[0])
                except IndexError:
                    i -= 1
                    break
            yield from client.send_message(message.channel,str(i+1)+" reports cleaned")
    if message.content.startswith(prefix+'reroll') and serv and admin and (not restricted): #Still on Developement
        if True: return #Avoid usage of this
        #Validation
        valid = None
        yield from client.send_message(message.channel,message.author.mention+"\n**The requested command is a dangerous command and will restart the minecraft server, it will also delete player data so do not use it for troll !\n:warning: Are you sure you want to run this command, answer 'Yes' to run it (this request will timeout in 30s) :warning:**")
        valid = yield from client.wait_for_message(timeout=30.0,author=message.author,channel=message.channel,content="Yes")
        if valid is None: return
        yield from client.send_message(message.channel,":warning: **Starting Reroll Operation** :warning:")
        logf.append("/reroll","Starting a reroll")
        #Get UUID
        api = MojangAPI()
        pseudo = message.content.replace(prefix+'reroll ',"")
        uuid = api.get_uuid(pseduo)
        logf.append("/reroll","uuid to reroll : "+uuid+" - "+pseudo)
        valid = None
        yield from client.send_message(message.channel,"The following UUID will be reroll :\n```diff\n+"+uuid+" ("+pseudo+")\n```\nAnswer 'STOP' to interupt the reroll (timeout in 60s)")
        valid = yield from client.wait_for_message(timeout=60.0,author=message.author,channel=message.channel,content="STOP")
        if valid is not None:
            logf.append("/reroll","interupted")
            yield from client.send_message(message.channel,"Reroll canceled")
            return
        #Shutdown Server
        logf.append("/reroll","Shutdown server")
        #Remove files
        logf.append("/reroll","removing files")
        directory = "../mc-instances/mc-57da87a88eec5/"
        data_dir = directory+"Gaea/playerdata/"
        uuid_file = uuid[:8]+"-"+uuid[8:12]+"-"+uuid[12:16]+"-"+uuid[16:20]+"-"+uuid[20:]
        for i in [pseudo+".baub",pseudo+".baubback",pseudo+".thaum",pseudo+".thaumback","aether/"+uuid_file+".dat","spawning/"+uuid_file+".dat",uuid_file+".dat"]:
            if os.access(data_dir+i,os.F_OK):
                os.remove(data_dir+i)
                logf.append("/reroll","removed "+data_dir+i)
                yield from client.send_message(message.channel,"removed "+data_dir+i)
        #Unban
        logf.append("/reroll","Player unbanned")
        yield client.send_message(message.channel,"Player unbanned")
        #Reboot Server
        logf.append("/reroll","Reboot Server")
        yield client.send_message(message.channel,"End of reroll")
    #vocal commands
    if message.content.startswith(prefix+'vocal') and serv and (not restricted):
        msg = (message.content).replace(prefix+'vocal ',"")
        msg = msg.lower()
        if msg == "on" and not client.is_voice_connected(message.server):
            if message.author.voice.voice_channel is None:
                yield from client.send_message(message.channel,"Sorry "+message.author.mention+" You are not in a vocal channel")
                return
            if modo or (message.author.voice.voice_channel.id == "295693183046778880" and message.channel.id == "285558746162397184"):
                yield from vocalsys.join(message.author.voice.voice_channel,message.channel)
                yield from client.send_message(message.channel,"Join Vocal and binding to "+message.channel.mention)
            else:
                yield from client.send_message(message.channel,"Sorry "+message.author.mention+" You are not in the music channel")
##            vocal = True
##            vocalco = yield from client.join_voice_channel(message.author.voice.voice_channel)
##            vocaltimer = VocalTimeout(60)
##            vocaltimer.start()
        elif msg == "off" and client.is_voice_connected(message.server) and modo:
            yield from vocalsys.leave()
##            vocal = False
##            yield from vocalco.disconnect()
    if message.content.startswith(prefix+'play') and serv and (not restricted):
        if not vocalsys.vocal:
            yield from client.send_message(message.channel,message.author.mention+"Use /vocal on before using vocal commands")
            return
        tag = message.content.replace(prefix+'play ',"")
        if "https://www.youtube.com" in tag:
            url = tag
        else:
            query = urllibp.urlencode({"search_query":tag})
            html = urllibr.urlopen("http://www.youtube.com/results?"+query)
            results = re.findall(r'href=\"\/watch\?v=(.{11})', html.read().decode())
            url = "http://www.youtube.com/watch?v=" + results[0]
            print(url)
##            tag = tag.split(" ")
##            while "" in tag: tag.remove("")
##            url = "https://www.youtube.com/results?search_query="
##            first = True
##            for i in tag:
##                if not first: url += "+"
##                url += i
##                first = False
##            url += "&page=1"
        yield from vocalsys.append(url)
        yield from client.send_message(message.channel,"Enqueued song : ```"+vocalsys.queue[-1].title+" by "+vocalsys.queue[-1].uploader+"```")
        vocalsys.play()
    if message.content.startswith(prefix+'soundeffect') and serv and modo and (not restricted):
        if not vocalsys.vocal:
            yield from client.send_message(message.channel,message.author.mention+"Use /vocal on before using vocal commands")
            return
        yield from vocalsys.append("Music/"+message.content.replace(prefix+'soundeffect ',""),False)
        vocalsys.play()
    if message.content.startswith(prefix+'skip') and serv and (not restricted):
        vocalsys.skip()
        #yield from client.send_message(message.channel,"Song has been skipped")
    if message.content.startswith(prefix+'showqueue') and serv and (not restricted):
        if vocalsys.current is not None:
            cur = "Currently Playing : **"+vocalsys.current.title+"** by "+vocalsys.current.uploader+"\n"
            #except: cur = "Currently Playing : **Sound Effect**\n"
        else:
            cur = "**No currently playing song**"
        string = "Vocal Queue :```diff\n"
        for i in vocalsys.queue:
            try: string += ("+"+i.title+" by "+i.uploader+"\n")
            except: string += ("+Sound Effect\n")
        string += "```"
        if len(vocalsys.queue) == 0: string="```diff\n-Empty Queue\n```"
        yield from client.send_message(message.channel,cur+string)
    #helping commands
    if message.content.startswith(prefix+'help'):
        if fr: f = open("help_FR.txt","r")
        else: f = open("help_EN.txt","r")
        yield from client.send_message(message.author,f.read())
        f.close()
        if serv:
            if fr: yield from client.send_message(message.channel,"Je t'ai envoyé un message privé "+message.author.mention)
            else: yield from client.send_message(message.channel,"I've sent you a private message "+message.author.mention)
    if message.content.startswith(prefix+'rules'):
        if modo:
            fr = ("FR" in message.content)
            chan = message.channel
        else:
            chan = message.author
        if fr: f = open("Rules_FR.txt","r")
        else: f = open("Rules_EN.txt","r")
        yield from client.send_message(chan,f.read())
        f.close()
        if (not modo) and serv:
            if fr: yield from client.send_message(message.channel,"Je t'ai envoyé un message privé "+message.author.mention)
            else: yield from client.send_message(message.channel,"I've sent you a private message "+message.author.mention)
    if message.content.startswith(prefix+'debug') and message.author == message.server.owner:
        msg = (message.content).replace(prefix+'debug ',"")
        print("running debug instruction : "+msg)
        logf.append("/debug","running debug instruction : "+msg)
        exec(msg)
##    ###DEBUG###
##    for i in message.server.members:
##        if str(i.id) not in lang:
##            lang[str(i.id)] = "EN"
##            channel = discord.utils.get(client.get_all_channels(), server__name='Skycraft', name='general')
##            yield from client.send_message(channel,"Welcome to "+i.mention)
##            f = open("welcome.txt","r")
##            yield from client.send_message(i,f.read())
##            f.close()
##    ###FIN DEBUG###
    yield from client.change_presence(game=statut)
    logf.stop()
    save_data()

@client.event
@asyncio.coroutine
def on_member_join(member):
    global lang
    logf.restart()
    logf.append("Join",str(member)+" has joined the server")
    lang[str(member.id)] = "EN"
    channel = discord.utils.get(client.get_all_channels(), server__name='Skycraft', name='general')
    yield from client.send_message(channel,"Welcome to "+member.mention)
    f = open("welcome.txt","r")
    yield from client.send_message(member,f.read())
    f.close()
    logf.stop()
    save_data()

@client.event
@asyncio.coroutine
def on_member_remove(member):
    global lang
    logf.restart()
    logf.append("Leave",str(member)+" has left the server")
    del(lang[str(member.id)])
    channel = discord.utils.get(client.get_all_channels(), server__name='Skycraft', name='general')
    yield from client.send_message(channel,member.mention+" has left us")
    logf.stop()
    save_data()

@asyncio.coroutine
def main_task():
    yield from client.login("MjM0NzAzOTQ5NDMxNzAxNTE1.C7GGhg.Wu8emIflGvVLm7GejPay_U8Bufg")
    yield from client.connect()
    yield from client.wait_until_ready()

def launch():
    global logf,prefix,config,lang,strikes,guild,guildlink,report,pray
    logsys = LogSystem()
    logsys.limit = 20
    logsys.directory = "Logs/local"
    tps = time.localtime()
    logf = Logfile(str(tps.tm_mday)+"_"+str(tps.tm_mon)+"_"+str(tps.tm_year)+"_"+str(tps.tm_hour)+"_"+str(tps.tm_min)+"_"+str(tps.tm_sec),logsys)
    logf.start()
    logf.append("Initializing","Bot initialization...")
    config = INI()
    config.load("config")
    prefix = config.section["main"]["prefix"]
    lang = convert_str_into_dic(config.section["main"]["lang"])
    strikes = convert_str_into_dic(config.section["main"]["strikes"])
    for i in strikes.keys():
        strikes[i] = int(strikes[i])
    guild = convert_str_into_dic(config.section["main"]["guild"])
    guildlink = convert_str_into_dic(config.section["main"]["guild_link"])
    report = convert_str_into_ls_spe(config.section["main"]["report"])
    pray = dict(config.section["gods"])
    for i in pray.keys():
        pray[i] = convert_str_into_ls_spe(pray[i])
    logf.append("Initializing","Bot initialized successful")
    logf.stop()

launch()
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main_task())
except:
    loop.run_until_complete(client.logout())
finally:
    loop.close()
