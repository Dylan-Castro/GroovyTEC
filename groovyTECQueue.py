import discord,asyncio
from queue import Queue

class GroovyTECQueue:
  # Preparando Ambiente
  songsQueue = Queue(maxsize = 0)
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
      if not self.songsQueue.empty():        
        self.currentSong = self.songsQueue.get()
        asyncio.run_coroutine_threadsafe(self.playCurrentSong(), self.bot.loop)
      else:
        self.currentSong = None
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
      self.songsQueue.put(song)
      await self.getCurrentSong().getCtx().send("Se agregó al queue")


  def clearQueue(self):
    self.songsQueue.clear()

  
  async def replayLastSong(self):
    try:
      if self.getCurrentSong() == None:
        self.currentSong = self.lastSong
        print("test")
        await self.playCurrentSong()
      else:
        await self.getCurrentSong().getCtx().send("Aun hay una cancion en curso oe gil.")
    except:
        await self.getCurrentSong().getCtx().send("No se pudo reproducir la cancion mi king.")