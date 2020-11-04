import datetime
import random
import requests
import time
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from tools.eventhandler import event_handler


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
DJANGO_URL = os.getenv('BOT_DJANGO_URL')

bot = commands.Bot(command_prefix='!')
user_ids = []


@bot.command(name='roll', help='Roll a card')
async def roll(ctx):
    _handle_user(ctx)
    # Get data from server
    resp = requests.post(f'{DJANGO_URL}/cards/roll/', data={'user_id': ctx.message.author.id})
    print(resp.json())
    if resp.status_code == 400:
        await ctx.send(f"{ctx.message.author.mention}: You have no more rolls left")
        return
    data = resp.json()
    # Format message
    embed = _create_embed(data)

    # Handle message
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    event_handler.append(msg, data)


@bot.event
async def on_reaction_add(reaction, user):
    # _handle_user(ctx)
    if user.bot is False and reaction.emoji == "👍": # AND AUTHER IS NOT SELF
        card = event_handler.get_card_by_msg(reaction.message)
        if card:
            # Claim a card
            resp = requests.post(f'{DJANGO_URL}/cards/claim/', data={
                'user_id': user.id,
                'card_id': card['id'],
            })
            print(resp.json())
            if resp.status_code == 400:
                print(resp.json())
                await reaction.message.channel.send(f"{user.mention}: You have no more claims")
                return
            # Get updated card information
            resp = requests.get(f'{DJANGO_URL}/cards/{card["id"]}/')
            print(resp.json())
            resp.raise_for_status()
            data = resp.json()
            # Update the card
            embed = _create_embed(data)
            await reaction.message.edit(embed=embed)
            print('message was updated')


@bot.event
async def on_ready():
    global user_ids # Ensures the assignment of user_ids applies to the global variable
    print("Connected")

    resp = requests.get(f'{DJANGO_URL}/users/')
    resp.raise_for_status()

    user_ids = [user['id'] for user in resp.json()]
    print('User ids found on the django server: ', user_ids)


def _handle_user(ctx):
    # get the discord user id
    user_id = int(ctx.message.author.id)
    # see if discord user id is in user_ids
    if user_id in user_ids:
        pass
    else:
        # Create a user
        resp = requests.post(f'{DJANGO_URL}/users/', data={
            'id': ctx.message.author.id,
            'name': ctx.message.author.name,
            'rolls': 10,
            'claims': 10,
            # 'avatar_url': ctx.message.author.avatar_url,
        })
        print(resp.json())
        resp.raise_for_status()
        user_ids.append(ctx.message.author.id)


def _create_embed(card):
    embed = discord.Embed(
        title=f"{card['name']} with the {card['weapon']}",
        # description="description",
    )
    embed.set_footer(text=f"Owned by {card['user']['name']}" if card['user'] else "", icon_url="https://i.pinimg.com/originals/5b/b4/8b/5bb48b07fa6e3840bb3afa2bc821b882.jpg")
    embed.set_image(url=f'http://vrmasterleague.com{card["image"]}')
    return embed


bot.run(TOKEN)