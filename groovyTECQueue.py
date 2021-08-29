import discord,asyncio
from queue import Queue

class GroovyTECQueue:
  # Preparando Ambiente
  songsQueue = []
  currentSong = None
  lastSong = None
  bot = None
  # Constantes
  FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
  

  def setBot(self, bot):
    self.bot = bot
  

  def getCurrentSong(self):
    return self.currentSong


  def nextSong(self):
    try:
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
        await self.getCurrentSong().getCtx().send(mensaje)
      elif not self.songsQueue:
        mensaje = "** No hay canciones en espera papi **"
        await self.getCurrentSong().getCtx().send(mensaje)
      #else:
        #mensaje = "** No hay canciones **"
        #await 
    except Exception as e:
      print(e)

  async def playCurrentSong(self):
    voice = self.getCurrentSong().getClient()
    voice.play(discord.FFmpegPCMAudio(self.getCurrentSong().getFilenameUrl(), **self.FFMPEG_OPTIONS), after = lambda e:self.nextSong())
    self.lastSong = self.getCurrentSong()

    await self.getCurrentSong().getCtx().send('**Sonando para tí mi king:**\n {title} \n {link}'.format(title=self.getCurrentSong().getTitle(),link=self.getCurrentSong().getYoutubeUrl()))


  async def addSongToQueue(self, song):
    if self.getCurrentSong() == None:
      self.currentSong = song
      await self.playCurrentSong()
    else:
      self.songsQueue.append(song)
      await self.getCurrentSong().getCtx().send("**Se agregó **"+song.getTitle()+"** al queue**")


  def clearQueue(self):
    self.songsQueue.clear()

  async def replayLastSong(self):
    try:
      if self.getCurrentSong() == None:
        self.currentSong = self.lastSong
        await self.playCurrentSong()
      else:
        await self.getCurrentSong().getCtx().send("Aun hay una canción en curso kza.")
    except:
        await self.getCurrentSong().getCtx().send("No se pudo reproducir la canción mi king.")
  
  def pauseSong(self):
    if self.getCurrentSong().getClient().is_playing():
      self.getCurrentSong().getClient().pause()

  def resumeSong(self):
    if self.getCurrentSong().getClient().is_paused():
      self.getCurrentSong().getClient().resume()

  def stopSong(self):
    if self.songsQueue:
      self.clearQueue()
    self.getCurrentSong().getClient().stop()