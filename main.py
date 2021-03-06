import youtubeUtil, discord
from musicObject import MusicObject
from groovyTECQueue import GroovyTECQueue
from discord.ext import commands,tasks
import os,psutil
from dotenv import load_dotenv
from server import keep_alive
from datetime import datetime
import pytz

#Constantes
botName= "GroovyTEC"
botId = 880231421040541787
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

# Se prepara el ambiente
DISCORD_TOKEN = os.environ['discord_token']

intents = discord.Intents().all()
#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='-',intents=intents)
groovyTECQueue = GroovyTECQueue()
groovyTECQueue.setBot(bot)
load_dotenv()

#Lista de Eventos
@bot.event
async def on_ready():
  print("GroovyTEC está ready!")

@bot.event
async def on_voice_state_update(member, before, after):
  global groovyTECQueue
  if member.bot == True and member.id == botId and before.channel == None:
    guardarEnLog("Bot entrando a las: "+ datetime.now(pytz.timezone("America/Lima")).strftime("%d/%m/%Y %H:%M:%S"))  
    groovyTECQueue.createTask()
    
  if member.bot == True and member.id == botId and after.channel == None: 
    guardarEnLog("Bot saliendo a las: "+ datetime.now(pytz.timezone("America/Lima")).strftime("%d/%m/%Y %H:%M:%S"))
    if groovyTECQueue.currentTask != None: 
      groovyTECQueue.currentTask.cancel()
      groovyTECQueue.clearVars()

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
@bot.command(name='test', aliases=['t'], help='Pa testear mi pana')
async def test(ctx):
    actualizarContexto(ctx)
    embed = discord.Embed(title="", description="Ta fino mi rey", color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command(name='leave', aliases=['l'], help='Para hacer que se quite del canal')
async def leave(ctx):
    actualizarContexto(ctx)
    voice_client = ctx.message.guild.voice_client
    if voice_client == None:
      await groovyTECQueue.sendMessage("No estoy conectado al  canal de voz mi chamo.")
    else:
      if ctx.author.voice.channel != ctx.channel.guild.voice_client.channel:
        raise discord.ext.commands.CommandError(botName+" ya se encuentra en uso en otro canal de voz.")
      else:
        await groovyTECQueue.sendMessage("A mimir Zzz :sleeping:")
        await voice_client.disconnect()
        
        

@bot.command(name='play', aliases=['p'], help='Para reproducir una canción')
async def play(ctx,*url):
    try :      
      global groovyTECQueue
      actualizarContexto(ctx)     
      cancion = ""
      if type(url) == tuple and len(url)==0:
        if ctx.channel.guild.voice_client.is_playing():
          return await groovyTECQueue.pauseSong()
        else:
          return await groovyTECQueue.resumeSong()
      elif type(url) == tuple and len(url)!=0:
        for palabra in url:
          cancion += palabra
          cancion += " "
      else:
        cancion = url

      #Se busca el video declarado
      async with ctx.typing():
        data = await youtubeUtil.YTDLSource.from_url(cancion, loop=bot.loop, stream=True)
      
      #Se crea el objecto musica
      musicObject = MusicObject(data['filename'],data['webpage_url'],data['title'],data['duration'],data['thumbnail'])

      #Se agrega al queue
      await groovyTECQueue.addSongToQueue(musicObject)
    except:
        await groovyTECQueue.sendMessage("No se pudo reproducir la canción mi king.")


@bot.command(name='replay', aliases=['r'], help='Para reproducir la ultima canción')
async def replay(ctx):
    try:
      global groovyTECQueue
      actualizarContexto(ctx)
      await groovyTECQueue.replayLastSong()
    except:
      await groovyTECQueue.sendMessage("No se pudo reproducir la canción mi king.")

@bot.command(name="queue", aliases=['q'], help="Muestra la cola de canciones")
async def queue(ctx):
    actualizarContexto(ctx)
    await groovyTECQueue.showQueue()
    
@bot.command(name="pause", help="Detiene la canción actual")
async def pause(ctx):
    global groovyTECQueue
    actualizarContexto(ctx)
    await groovyTECQueue.pauseSong()

@bot.command(name="resume", aliases=['continue'], help="Reanuda la canción actual")
async def resume(ctx):
    global groovyTECQueue
    actualizarContexto(ctx)
    await groovyTECQueue.resumeSong()

@bot.command(name="stop", aliases=['s'], help="Detiene la canción")
async def stop(ctx):
    global groovyTECQueue
    actualizarContexto(ctx)
    await groovyTECQueue.stopSong()

@bot.command(name="skip", help="Para pasar a la siguiente canción")
async def skip(ctx):
    global groovyTECQueue
    actualizarContexto(ctx)
    await groovyTECQueue.skipSong()

@bot.command(name="resources", help="Para ver los recursos del servidor")
async def resources(ctx):
    actualizarContexto(ctx)
    mensaje = """Bajando pepa con:\n
    CPU: {0}%\n
    RAM: {1}%""".format(psutil.cpu_percent(),psutil.virtual_memory().percent)
    await groovyTECQueue.sendMessage(mensaje)

@bot.command(name="loop", help="Para poner en loop la cancion actual")
async def loop(ctx):
    global groovyTECQueue
    actualizarContexto(ctx)
    await groovyTECQueue.loopSong()

@bot.command(name="current", help="Para conocer información de la canción actual")
async def current(ctx):
    actualizarContexto(ctx)
    await groovyTECQueue.showCurrent()

#Funciones Utiles
@loop.before_invoke
@pause.before_invoke
@play.before_invoke
@queue.before_invoke
@replay.before_invoke
@resources.before_invoke
@resume.before_invoke
@skip.before_invoke
@stop.before_invoke
@test.before_invoke
@current.before_invoke
async def validarDisponibilidadDelBot(ctx):
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

def actualizarContexto(ctx):
  global groovyTECQueue
  groovyTECQueue.setContext(ctx)

def guardarEnLog(mensaje):
  file = open('log.txt', 'a')
  file.write(mensaje + "\n")
  file.close()

if __name__ == "__main__" :
    keep_alive()
    bot.run(DISCORD_TOKEN)
