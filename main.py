import youtubeUtil, discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
from server import keep_alive
song_queue = []
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


load_dotenv()

# Get the API token from the .env file.
DISCORD_TOKEN = os.environ['discord_token']

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='-/',intents=intents)

#Lista de Eventos
@bot.event
async def on_ready():
    print("GroovyTEC está ready!")

# Lista de Comandos
@bot.command(name='test', help='Pa testear mi pana')
async def test(ctx):
    await ctx.send("Ta fino mi rey.")

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='l', help='Para hacer que se quite del canal')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("No estoy conectado al canal de voz mi chamo.")

@bot.command(name='p', help='Para reproducir una cancion')
async def play(ctx,*url):
    try :
      cancion = ""
      if type(url) == tuple:
        for palabra in url:
          cancion += palabra
          cancion += " "
      else:
        cancion = url

      voice_channel = ctx.author.voice.channel
      voice = ctx.channel.guild.voice_client
      if voice is None:
          voice = await voice_channel.connect()
      elif voice.channel != voice_channel:
          voice.move_to(voice_channel)

      async with ctx.typing():
        data = await youtubeUtil.YTDLSource.from_url(cancion, loop=bot.loop, stream=True)
        voice.play(discord.FFmpegPCMAudio(data['filename'], **FFMPEG_OPTIONS, after=lambda e: play_next(ctx)))
        await ctx.send('**Sonando para tí mi king:**\n {title} \n {link}'.format(title=data['title'],link=data['webpage_url']))
    except:
        await ctx.send("No se pudo reproducir la cancion mi king.")


if __name__ == "__main__" :
    keep_alive()
    bot.run(DISCORD_TOKEN)
