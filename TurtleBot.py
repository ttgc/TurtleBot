#!usr/bin/env python3.4
#-*-coding:utf-8-*-

import discord
import asyncio
import logging
import os
import time
from logfile import *
from INIfiles import *

global prefix,logf,config,lang,guild
prefix = "/"

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

def save_data():
    global prefix,config,strikes,guild,guildlink
    config.key_add("main","prefix",prefix)
    config.key_add("main","lang",str(lang))
    config.key_add("main","strikes",str(strikes))
    config.key_add("main","guild",str(guild))
    config.key_add("main","guild_link",str(guildlink))
    config.save("config")

client = discord.Client()

@client.event
@asyncio.coroutine
def on_ready():
    global logf
    yield from client.change_presence(game=discord.Game(name="/help"))
    logf.restart()
    logf.append("Initializing","Bot is now ready")
    logf.stop()

@client.event
@asyncio.coroutine
def on_message(message):
    global prefix,logf,lang,strikes,guild,guildlink
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
    if message.content.startswith(prefix+'profil'):
        if len(message.mentions) != 0:
            profil = message.mentions[0]
        else:
            profil = message.author
        col = discord.Color(0).green()
        try: strik = strikes[str(profil.id)]
        except KeyError: strik = 0
        if not serv: rol = "Undefined"
        else:
            if profil.top_role == hierarchy[0]: rol = "Admin"
            elif profil.top_role == hierarchy[1]: rol = "Modo"
            elif profil.top_role == hierarchy[2]: rol = "Dev"
            elif profil.top_role == hierarchy[3]: rol = "VIP"
            else: rol = "Player"
        try: gd = guild[str(profil.id)]
        except KeyError: gd = "Indep"
        embd = discord.Embed(title=profil.name,description="User Profile",colour=profil.top_role.color)
        embd.set_footer(text="Skycraft Discord Profile : http://skycraft.tech/",icon_url="http://skycraft.tech/wp-content/uploads/2016/08/cropped-Computercraft.png")
        embd.set_image(url=profil.avatar_url)
        embd.add_field(name="Language :",value=lang[str(profil.id)],inline=True)
        embd.add_field(name="Rank :",value=rol,inline=True)
        embd.add_field(name="Strike :",value=str(strik),inline=True)
        embd.add_field(name="Faction :",value=gd,inline=True)
        yield from client.send_message(message.channel,embed=embd)
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
                    yield from client.send_message(message.channel,i.mention+"\n```\nVous avez reçu de la part de l'équipe un avertissement !\nVous avez reçu cet avertissement pour ne pas avoir respecté les regles d'utilisation du serveur discord visible en utilisant la commande '/rules'\nEn cas de récidive des sanctions seront automatiquement appliquées pouvant aller jusqu'au kick ou ban def suivant le tableau suivant :\n1 Strike = rien\n2 Strikes = rien\n3 Strikes = restriction\n4 Strikes = kick\n5 Strikes = Perma ban\n\nVeuillez respecter les règles du serveur pour éviter tout nouvel avertissement\nMerci de votre compréhension\n```")
                else:
                    yield from client.send_message(message.channel,i.mention+"\n```\nYou have got a strike from the staff !\nYou have got it for unrespect of the rules of the discord server that you can claim with the '/rules' command\nIn case of a new strike, you would probably get an automatic penalization including kick or perma ban following this table :\n1 Strike = Nothing\n2 Strikes = Nothing\n3 Strikes = Restrictions\n4 Strikes = kick\n5 Strikes = Perma ban\n\nPlease respect the rules of the server to avoid a new strike\nThanks to your understanding\n```")
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
        msg = f.read().split("\n\n")
        for i in msg:
            yield from client.send_message(chan,i)
        f.close()
        if (not modo) and serv:
            if fr: yield from client.send_message(message.channel,"Je t'ai envoyé un message privé "+message.author.mention)
            else: yield from client.send_message(message.channel,"I've sent you a private message "+message.author.mention)
    if message.content.startswith(prefix+'debug') and message.author == message.server.owner:
        msg = (message.content).replace(prefix+'debug ',"")
        print("running debug instruction : "+msg)
        logf.append("/debug","running debug instruction : "+msg)
        exec(msg)
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

def launch():
    global logf,prefix,config,lang,strikes,guild,guildlink
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
    guild = convert_str_into_dic(config.section["main"]["guild"])
    guildlink = convert_str_into_dic(config.section["main"]["guild_link"])
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
