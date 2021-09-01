import discord,asyncio
from queue import Queue

class GroovyTECQueue:
  # Preparando Ambiente
  songsQueue = []
  currentSong = None
  lastSong = None
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
  

  def getCurrentSong(self):
    return self.currentSong


  def nextSong(self):
    try:
      if self.loop:
        asyncio.run_coroutine_threadsafe(self.playCurrentSong(), self.bot.loop)
      else:
        if self.songsQueue:        
          self.currentSong = self.songsQueue.pop(0)
          asyncio.run_coroutine_threadsafe(self.playCurrentSong(), self.bot.loop)
        else:        
          self.currentSong = None
    except Exception as e:
      print(e)   

  async def showQueue(self):
    try:
      if self.songsQueue:
        canciones = self.songsQueue
        mensaje = "** Este es el queue:\n**"
        for cancion in canciones:
          mensaje += "- "+cancion.getTitle()+"\n"
        await self.ctx.send(mensaje)
      elif not self.songsQueue:
        mensaje = "** No hay canciones en espera papi **"
        await self.ctx.send(mensaje)
      #else:
        #mensaje = "** No hay canciones **"
        #await 
    except Exception as e:
      print(e)

  async def playCurrentSong(self):
    self.client.play(discord.FFmpegPCMAudio(self.getCurrentSong().getFilenameUrl(), **self.FFMPEG_OPTIONS), after = lambda e:self.nextSong())
    self.lastSong = self.getCurrentSong()
    if not self.loop:
      await self.ctx.send('**Sonando para tí mi king:**\n {title} \n {link}'.format(title=self.getCurrentSong().getTitle(),link=self.getCurrentSong().getYoutubeUrl()))


  async def addSongToQueue(self, song):
    if self.getCurrentSong() == None:
      self.currentSong = song
      await self.playCurrentSong()
    else:
      self.songsQueue.append(song)
      await self.ctx.send("**Se agregó **"+song.getTitle()+"** al queue**")


  def clearQueue(self):
    self.songsQueue.clear()

  async def replayLastSong(self):
    try:
      if self.getCurrentSong() == None:
        self.currentSong = self.lastSong
        await self.playCurrentSong()
      else:
        await self.ctx.send("Aun hay una canción en curso kza.")
    except:
        await self.ctx.send("No se pudo reproducir la canción mi king.")
  
  def pauseSong(self):
    if self.client.is_playing():
      self.client.pause()

  def resumeSong(self):
    if self.client.is_paused():
      self.client.resume()

  def stopSong(self):
    if self.songsQueue:
      self.clearQueue()
    self.client.stop()
    self.currentSong = None

  async def skipSong(self):
    if self.getCurrentSong() != None:
      if self.songsQueue:
        await self.ctx.send("Cambiando a la siguiente cancion :track_next:")
        self.client.stop()     
      else:
        await self.ctx.send("**No hay más canciones en espera en el queue**")
        self.client.stop()

  async def loopSong(self):
    if self.getCurrentSong() != None:
      if self.loop:
        self.loop = False
        await self.ctx.send("Se detuvo el loop, volviendo a las canciones del queue mi ciela :nail_care:")    
      else:
        self.loop = True
        await self.ctx.send("**Reproduciendo en loop **"+self.getCurrentSong().getTitle())
        

        