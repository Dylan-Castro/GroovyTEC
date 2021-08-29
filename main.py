import youtubeUtil, discord,groovyTECQueue
from musicObject import MusicObject
from groovyTECQueue import GroovyTECQueue
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
from server import keep_alive

#Constantes
botName= "GroovyTEC"
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

# Se prepara el ambiente
DISCORD_TOKEN = os.environ['discord_token']

intents = discord.Intents().all()
intents.members = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='-/',intents=intents)
groovyTECQueue = GroovyTECQueue()
groovyTECQueue.setBot(bot)

load_dotenv()

#Lista de Eventos
@bot.event
async def on_ready():
  print("GroovyTEC está ready!")

@bot.event
async def on_member_join(member):
  await print(f'{member} has joined the server.')

@bot.event
async def on_member_remove(member):
  print(f'{member} has leaved the server.')
  await member.send('Private message')

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)

# Lista de Comandos
@bot.command(name='test', help='Pa testear mi pana')
async def test(ctx):
    await ctx.send("Ta fino mi rey.")

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

      async with ctx.typing():
        #Se busca el video declarado
        data = await youtubeUtil.YTDLSource.from_url(cancion, loop=bot.loop, stream=True)
        
        #Se crea el objecto musica
        musicObject = MusicObject(data['filename'],data['webpage_url'],data['title'],ctx)

        #Se agrega al queue
        await groovyTECQueue.addSongToQueue(musicObject)
    except:
        await ctx.send("No se pudo reproducir la cancion mi king.")


@bot.command(name='r', help='Para reproducir la ultima cancion')
async def replay(ctx):
    try:
      await groovyTECQueue.replayLastSong()
    except:
      await ctx.send("No se pudo reproducir la cancion mi king.")

#Funciones Utiles
@play.before_invoke
async def ensure_voice(ctx):
  if ctx.author.voice is None:
    raise discord.ext.commands.CommandError("No estas conectado a un canal de voz.")
  elif ctx.voice_client is None:
      await ctx.author.voice.channel.connect()
  elif ctx.author.voice.channel != ctx.channel.guild.voice_client.channel:
    raise discord.ext.commands.CommandError(botName+" ya se encuentra en uso en otro canal de voz.")
  elif ctx.author.voice.channel == ctx.channel.guild.voice_client.channel:
    pass
  else:
    raise discord.ext.commands.CommandError("Algo salió mal xd.")

if __name__ == "__main__" :
    keep_alive()
    bot.run(DISCORD_TOKEN)
