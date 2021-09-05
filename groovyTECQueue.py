import discord,asyncio
import time
from async_timeout import timeout
from queue import Queue

class GroovyTECQueue:
  # Preparando Ambiente
  songsQueue = asyncio.Queue()
  next = asyncio.Event()
  currentSong = None
  lastSong = None
  start_timestamp = None
  elapsed_time = 0
  loop = False
  
  # Variables Discord
  bot = None
  ctx = None
  client = None
  channel = None
  # Constantes
  FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
  
  def setContext(self, ctx):
    self.channel = ctx.author.voice.channel
    self.client = ctx.channel.guild.voice_client
    self.ctx = ctx

  def setBot(self, bot):
    self.bot = bot

  async def enviarMensaje(self, mensaje, titulo = ""):
    embed=discord.Embed(title=titulo,description=mensaje)
    return await self.ctx.send(embed=embed)

  def getCurrentSong(self):
    return self.currentSong

  async def showQueue(self):
    try:
      if self.songsQueue.qsize() != 0:
        canciones = self.songsQueue._queue
        mensaje = "** Este es el queue:\n**"
        for cancion in canciones:
          mensaje += "- "+cancion.getTitle()+"\n"
        await self.enviarMensaje(mensaje)
      else:
        mensaje = "** No hay canciones en espera papi **"
        await self.enviarMensaje(mensaje)
      #else:
        #mensaje = "** No hay canciones **"
        #await 
    except Exception as e:
      print(e)

  async def playCurrentSong(self):

    await self.bot.wait_until_ready()
    while True:
      self.next.clear()
      if not self.loop:
        try:
          async with timeout(500):  # 5 minutos
            self.currentSong = await self.songsQueue.get()
        except asyncio.TimeoutError:
          await self.enviarMensaje("**Grupo muerto?? Ñafo como dirían los hipócritas** :wave:")
          return await self.client.disconnect()
        
      self.client.play(discord.FFmpegPCMAudio(self.currentSong.getFilenameUrl(), **self.FFMPEG_OPTIONS), after=lambda e: self.bot.loop.call_soon_threadsafe(self.next.set))
      self.start_timestamp = time.perf_counter()
      self.elapsed_time = 0

      if not self.loop:
        message = await self.enviarMensaje('**Sonando para tí mi king:**\n {title} \n {link}'.format(title=self.currentSong.getTitle(),link=self.currentSong.getYoutubeUrl()))
        self.lastSong = self.currentSong

      await self.next.wait()
      await message.delete()
      
      if self.songsQueue.qsize() == 0 and not self.loop:
        self.currentSong = None


  async def addSongToQueue(self, song):
    await self.songsQueue.put(song)
    if not self.getCurrentSong() == None:
      await self.enviarMensaje("**Se agregó **"+song.getTitle()+"** al queue**")

  async def showCurrent(self):
    currentSong = self.getCurrentSong()
    if currentSong:
      # Construcción del tiempo total 
      duration = currentSong.getDuration()
      seconds = duration % (24 * 3600) 
      hour = seconds // 3600
      seconds %= 3600
      minutes = seconds // 60
      seconds %= 60
      if hour > 0:
          songTime = "%d:%02d:%02d" % (hour, minutes, seconds)
      else:
          songTime = "%02d:%02d" % (minutes, seconds)
      # Construcción del tiempo actual
      if self.client.is_paused():
        current_elapsed_time = self.elapsed_time
      else:  
        current_elapsed_time = int(time.perf_counter()-self.start_timestamp) + self.elapsed_time
      seconds = current_elapsed_time % (24 * 3600) 
      hour = seconds // 3600
      seconds %= 3600
      minutes = seconds // 60
      seconds %= 60
      if hour > 0:
          current_elapsed_time = "%d:%02d:%02d" % (hour, minutes, seconds)
      else:
          current_elapsed_time = "%02d:%02d" % (minutes, seconds)
      
      await self.enviarMensaje(currentSong.getTitle()+"\n"+current_elapsed_time+"/"+songTime)
    else:
      await self.enviarMensaje("**No hay canciones sonando manito**")


  def clearQueue(self):
    while self.songsQueue.qsize() != 0:
        self.songsQueue.get_nowait()

  async def replayLastSong(self):
    try:
      if self.getCurrentSong() == None:
        await self.songsQueue.put(self.lastSong)
      else:
        await self.enviarMensaje("Aun hay una canción en curso kza.")
    except:
        await self.enviarMensaje("No se pudo reproducir la canción mi king.")
  
  async def pauseSong(self):
    if self.client.is_playing():
      self.elapsed_time += int(time.perf_counter()-self.start_timestamp)
      self.client.pause()
      await self.enviarMensaje("Pausado :pause_button:")

  async def resumeSong(self):
    if self.client.is_paused():
      self.start_timestamp = time.perf_counter()
      self.client.resume()
      await self.enviarMensaje("Resumiendo :play_pause:")

  async def stopSong(self):
    if self.songsQueue:
      self.clearQueue()
    if self.loop:
      self.loop = False
    self.client.stop()
    self.start_timestamp = None
    self.elapsed_time = 0
    self.currentSong = None
    await self.enviarMensaje("A mimir Zzz :sleeping:")

  async def skipSong(self):
    if self.getCurrentSong() != None:
      if self.songsQueue.qsize() != 0:
        if self.loop:
          self.currentSong = await self.songsQueue.get() 
        await self.enviarMensaje("Cambiando a la siguiente cancion :track_next:")
        self.elapsed_time = 0
        self.client.stop()                             
      else:
        await self.enviarMensaje("**No hay más canciones en espera en el queue**")
        self.client.stop()

  async def loopSong(self):
    if self.getCurrentSong() != None:
      if self.loop:
        self.loop = False
        await self.enviarMensaje("Se detuvo el loop, volviendo a las canciones del queue mi ciela :nail_care:")    
      else:
        self.loop = True
        await self.enviarMensaje("**Reproduciendo en loop **"+self.getCurrentSong().getTitle())
        

        