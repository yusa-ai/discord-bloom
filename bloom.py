import asyncio
import os
import re
from collections import defaultdict
from datetime import datetime

import aioschedule as schedule
import discord
from discord.ext import commands
from discord.utils import get
from emoji import EMOJI_ALIAS_UNICODE as emojis

token = os.getenv("DISCORD_BOT_TOKEN")

sessions = defaultdict(lambda: defaultdict(list))

bloom = commands.Bot(command_prefix='$', help_command=None)

async def send_sessions():
    current_day = datetime.today().weekday()
    current_time = datetime.now().strftime('%Hh%M')
    for i, session in enumerate(sessions[current_day][current_time]):
        if not session[0]:
            channel = bloom.get_channel(session[1][3])
            if channel:
                emb = discord.Embed(title='Début imminent', description=f'Le cours de {session[1][1]} va commencer !', color=0xf4abba)
                # mention role
                if session[1][0] is not None:
                    emb.add_field(name='Groupe :', value=f'{session[1][0]}', inline=False)
                # add link
                if session[1][2] is not None:
                    emb.add_field(name='Plateforme :', value=f'{session[1][2]}', inline=False)

                await channel.send(embed=emb)
                session[0] = True
            else:
                sessions[current_day][current_time].pop(i)

# TODO reset sessions at midnight

@bloom.event
async def on_ready():
    await bloom.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='les prochains cours ($help)'))
    print('BLOOM initialisé')
    schedule.every(3).seconds.do(send_sessions)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)

@bloom.command()
async def help(ctx):
    emb = discord.Embed(title='Aide', description='Liste des commandes de Bloom', color=0xf4abba)
    emb.set_thumbnail(url='https://ryanmalonzo.fr/chbsm.png')
    # cours
    emb.add_field(name='$cours', value='Ajoute un cours récurrent\nFormat : `$cours <nom_cours> <jour> <heure> [lien] [rôle]`', inline=True)
    emb.add_field(name='Exemple :', value='`$cours BPO lundi 14h00 https://zoom.us/ @101`')
    #aide
    emb.add_field(name='$help', value='Affiche cette aide', inline=False)

    emb.set_footer(text=u'\u00A9'+' Ryan Malonzo')
    await ctx.send(embed=emb)

@bloom.command()
async def cours(ctx, name, day, time, link=None, role=None):
    
    days = {
        'lundi': 0,
        'mardi': 1,
        'mercredi': 2,
        'jeudi': 3,
        'vendredi': 4,
        'samedi': 5,
        'dimanche': 6
    }

    if day.lower() not in days:
        emb = discord.Embed(title='Erreur', description=f'{ctx.author.mention} Le jour entré est-il bien en lettres (ex : lundi) ?', color=0xf4abba)
        await ctx.send(embed=emb)
    else:
        day = days[day]
    if len(time) == 5 and re.match(r'\d{2}h\d{2}', time):
        channel = ctx.channel.id
        session = [False, (role, name, link, channel)]
        sessions[day][time].append(session)

        emb = discord.Embed(title=emojis[':white_check_mark:']+' Nouveau cours ajouté', color=0xf4abba)
        await ctx.send(embed=emb)
        print(f'{name} {day} {time} {link} {role} {channel}')
    else:
        emb = discord.Embed(title='Erreur', description=f'{ctx.author.mention} L\'horaire entré doit suivre le format "HHhMM".', color=0xf4abba)
        await ctx.send(embed=emb)

    #await asyncio.sleep(3)
    #await ctx.message.delete()
    #await msg.delete()

bloom.run(token)
