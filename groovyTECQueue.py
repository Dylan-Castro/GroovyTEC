import musicObject,discord,asyncio
from queue import Queue

class GroovyTECQueue:
  # Preparando Ambiente
  songsQueue = Queue(maxsize = 0)
  currentSong = None
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
    except Exception as e:
        print(e)   
  
  async def playCurrentSong(self):
    print("test4")
    voice = self.getCurrentSong().getClient()
    voice.play(discord.FFmpegPCMAudio(self.getCurrentSong().getFilenameUrl(), **self.FFMPEG_OPTIONS), after = lambda e:self.nextSong())

    await self.getCurrentSong().getCtx().send('**Sonando para tí mi king:**\n {title} \n {link}'.format(title=self.getCurrentSong().getTitle(),link=self.getCurrentSong().getYoutubeUrl()))

  async def addSongToQueue(self, song):
    if self.getCurrentSong() == None:
      self.currentSong = song
      await self.playCurrentSong()
    else:
      self.songsQueue.put(song)
      print(self.songsQueue.qsize())
      await self.getCurrentSong().getCtx().send("Se agregó al queue")

  def clearQueue(self):
    self.songsQueue.clear()

    