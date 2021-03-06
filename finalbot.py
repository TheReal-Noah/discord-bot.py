import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import shutil

BOT_PREFIX = '*'

bot = commands.Bot(command_prefix=BOT_PREFIX)
bot.remove_command('help')

@bot.event
async def on_ready():
    game = discord.Game('songs and stuffs ')
    await bot.change_presence(status = discord.Status.online,activity=game,afk=True)
    print('{} has logged in'.format(str(bot.user)))

#ping
@bot.command()
async def ping(ctx):
    await ctx.send('my latency is {}ms'.format(bot.latency * 100))


#join
@bot.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")

    await ctx.send(f"Joined {channel}")

#leave
@bot.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"Left {channel}")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Don't think I am in a voice channel")

#play
@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, url: str):

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")



    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music playing")
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    await ctx.send("Getting everything ready now")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {'format': 'bestaudio/best',
    'postprocessors': [{'key':'FFmpegExtractAudio',
                        'preferredcodec':'mp3',
                        'preferredquality':'192'}],
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'outtmpl' : '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.7

    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname[0]}")
    print("playing\n")

#pause
@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing failed pause")
        await ctx.send("Music not playing failed pause")

#resume
@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")

#stop
@bot.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")
    else:
        print("No music playing failed to stop")
        await ctx.send("No music playing failed to stop")

#queue
queues = {}

@bot.command(pass_context=True, aliases=['q', 'que'])
async def queue(ctx, url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {'format': 'bestaudio/best',
    'postprocessors': [{'key':'FFmpegExtractAudio',
                        'preferredcodec':'mp3',
                        'preferredquality':'192'}],
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'outtmpl' : queue_path,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])
    await ctx.send("Adding song " + str(q_num) + " to the queue")

    print("Song added to queue\n")
#volume
@bot.command(pass_context=True, aliases=['v', 'vol'])
async def volume(ctx, volume: int):

    if ctx.voice_client is None:
        return await ctx.send("Not connected to voice channel")

    print(volume/100)

    ctx.voice_client.source.volume = volume / 100
    await ctx.send(f"Changed volume to {volume}%")

#whois
@bot.command(aliases = ['user','info'])
async def whois(ctx,member:discord.Member):
    try:
        embed = discord.Embed(title = member.name,description = member.mention,color = discord.Color.dark_magenta())
        embed.add_field(name ='ID',value = member.id,inline = False)
        mention = []
        for role in member.roles:
            if role.name != '@everyone':
                mention.append(role.mention)
        b = ', '.join(mention)
        embed.add_field(name = 'Top role',value = member.top_role,inline =False)
        embed.add_field(name = 'roles', value = b,inline = False)
        embed.set_thumbnail(url=member.avatar_url)
        
        embed.set_footer(icon_url = ctx.author.avatar_url,text = f"Requested by {ctx.author.name}")
        await ctx.send(embed = embed)
    except Exception:
        await ctx.send('mention them!!')



    




#help
@bot.command(aliases = ['helpuh','h'])
async def help(ctx):
    embed = discord.Embed(title ='help',description = 'this shows commands available',color = discord.Color.dark_red())
    embed.add_field(name = 'join',value = 'makes the bot join voice channel',inline = True)
    embed.add_field(name = 'play',value = 'starts playing music',inline = True)
    embed.add_field(name = 'queue',value = 'queues set of songs to play next',inline = True)
    embed.add_field(name = 'skip',value='skips to the next song from queue',inline = True)
    embed.add_field(name = 'pause',value = 'pauses the song',inline = True)
    embed.add_field(name = 'resume',value='resumes the song',inline = True)
    embed.add_field(name = 'stop',value ='stops the song',inline = True)
    embed.add_field(name = 'leave',value = 'leaves the voice channel',inline = True)
    embed.add_field(name = 'ping',value = 'shows the latency of the bot',inline = True)
    embed.add_field(name = 'volume',value = 'adjust the volume(enter in whole number)',inline = True)
    embed.add_field(name = 'whois',value = 'gives the avatar and id of the mentioned user',inline = True)
    await ctx.send(embed = embed)




bot.run('NzM0NDA5NTYxNTQ0NTg5NDMz.XxRSNA.DKefUBwAiyiyWbgGCZyOhV69KT4')
