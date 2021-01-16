import discord
from reply import Reply
import re
import sys
import pickle

tpath = "./data/tokenizer/tokenizer.pickle"
hpath = "./data/hparams/hparams.pickle"
mpath = [
    "./data/model/cp-0088.ckpt",
]
TOKEN = open("token.txt").read()
reply = Reply(tpath, hpath, mpath)
client = discord.Client()


@client.event
async def on_message(message):
    mention = message.author.mention + "\n"
    content = message.content
    user_name = message.author.display_name
    if message.author.bot:
        return
    elif client.user in message.mentions and "/help" in content:
        await message.channel.send(mention + reply.reply_help())
    elif client.user in message.mentions and "/image" in content:
        await message.channel.send(mention + reply.reply_image(content))
    elif client.user in message.mentions and "/tenki" in content:
        await message.channel.send(mention + reply.reply_forecast())
    elif client.user in message.mentions and "/news" in content:
        await message.channel.send(mention + reply.reply_news())
    elif client.user in message.mentions and "/clear" in content:
        try:
            if message.author.guild_permissions.administrator:
                await message.channel.purge()
                await message.channel.send(mention + "ログを削除しました")
        except:
            await message.channel.send(mention + "ログを削除できませんでした")
    elif client.user in message.mentions and "/kill" in content:
        await message.channel.send(mention + "プログラムを終了します")
        sys.exit()
    elif client.user in message.mentions:
        text, reaction = reply.reply_chat(user_name, content)
        if reaction:
            await message.add_reaction(reaction)
        await message.channel.send(mention + text)


client.run(TOKEN)