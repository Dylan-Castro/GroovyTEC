import discord,asyncio,time , youtubeUtil
from musicObject import MusicObject
from async_timeout import timeout
from queue import Queue
from urllib.parse import urlparse,parse_qs


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
  currentTask = None
  # Constantes
  FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
  #Personal Play list
  personalPlayList = None
    
  def setContext(self, ctx):
    self.channel = ctx.author.voice.channel
    self.client = ctx.channel.guild.voice_client
    self.ctx = ctx

  def setBot(self, bot):
    self.bot = bot

  def createTask(self):
    #Inicializa el queue si es que el bot a estado desconectado
    if self.currentTask == None:
      self.currentTask = asyncio.create_task(self.playCurrentSong())

  async def sendMessage(self, mensaje, thumbnail = "", titulo = ""):
    embed=discord.Embed(title=titulo,description=mensaje,color=discord.Color.purple())
    embed.set_thumbnail(url=thumbnail).set_image(url=thumbnail)
    return await self.ctx.send(embed=embed)

  def getCurrentSong(self):
    return self.currentSong

  async def checkExpireDateCurrentSong(self):
    try:
      parsed_url = urlparse(self.getCurrentSong().getFilenameUrl())
      expireTimeStamp = parse_qs(parsed_url.query)['expire'][0]
      if float(expireTimeStamp) < time.time():
        #Se busca el video vencido
        data = await youtubeUtil.YTDLSource.from_url(self.getCurrentSong().getYoutubeUrl(), loop=self.bot.loop, stream=True)
        #Se actualiza el link stream
        self.getCurrentSong().setFilenameUrl(data['filename'])
        if self.personalPlayList != None:
          if self.personalPlayList.currentMember != None:
            #Se actualiza la playlist
            self.personalPlayList.savePlayList(self.personalPlayList.currentMember, self.personalPlayList.playList)
    except:
      await self.sendMessage("No se pudo actualizar la cancion")

  async def showQueue(self):
    try:
      if self.songsQueue.qsize() != 0:
        canciones = self.songsQueue._queue
        mensaje = "** Este es el queue:\n**"
        for cancion in canciones:
          mensaje += "- "+cancion.getTitle()+"\n"
        await self.sendMessage(mensaje)
      else:
        mensaje = "** No hay canciones en espera papi. **"
        await self.sendMessage(mensaje)
      #else:
        #mensaje = "** No hay canciones **"
        #await 
    except Exception as e:
      print(e)

  async def playCurrentSong(self):
    while True:
      self.next.clear()
      if not self.loop:
        try:
          self.currentSong = await asyncio.wait_for(self.songsQueue.get(), 300) # 300 segundos
        except asyncio.TimeoutError:
          await self.sendMessage("**Grupo muerto?? Ñafo como dirían los hipócritas** :wave:")
          return await self.client.disconnect()
      
      await self.checkExpireDateCurrentSong()

      self.client.play(discord.FFmpegPCMAudio(self.currentSong.getFilenameUrl(), **self.FFMPEG_OPTIONS), after=lambda e: self.bot.loop.call_soon_threadsafe(self.next.set))
      self.start_timestamp = time.perf_counter()
      self.elapsed_time = 0

      message = None
      if not self.loop:
        message = await self.sendMessage('**Sonando para tí mi king:**\n {title} \n {link}'.format(title=self.currentSong.getTitle(),link=self.currentSong.getYoutubeUrl()),self.currentSong.getThumbnail())
        self.lastSong = self.currentSong

      await self.next.wait()
      #Se borrara el mensaje de la cancion
      if not message == None:
        await message.delete()

      if self.songsQueue.qsize() == 0 and not self.loop:
        self.currentSong = None
        #Se borrara la playlist si es que ha sido usada
        if self.personalPlayList != None:
          self.personalPlayList = None


  async def addSongToQueue(self, song):
    await self.songsQueue.put(song)
    if not self.getCurrentSong() == None:
      await self.sendMessage("**Se agregó **"+song.getTitle()+"** al queue**")

  async def showCurrent(self):
    if self.getCurrentSong() != None:
      # Construcción del tiempo total 
      duration = self.getCurrentSong().getDuration()
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
      
      await self.sendMessage(self.getCurrentSong().getTitle()+"\n"+current_elapsed_time+"/"+songTime)
    else:
      await self.sendMessage("**No hay canciones sonando manito**")


  def clearQueue(self):
    while self.songsQueue.qsize() != 0:
        self.songsQueue.get_nowait()

  async def replayLastSong(self):
    try:
      if self.lastSong == None:
        await self.sendMessage("No se ha tocado ninguna canción antes.")
      elif self.getCurrentSong() == None:
        await self.songsQueue.put(self.lastSong)
      else:
        await self.sendMessage("Aún hay una canción en curso kza.")
    except:
        await self.sendMessage("No se pudo reproducir la canción mi king.")
  
  async def pauseSong(self):
    if self.client.is_playing():
      self.elapsed_time += int(time.perf_counter()-self.start_timestamp)
      self.client.pause()
      await self.sendMessage("Pausado :pause_button:")

  async def resumeSong(self):
    if self.client.is_paused():
      self.start_timestamp = time.perf_counter()
      self.client.resume()
      await self.sendMessage("Resumiendo :play_pause:")

  async def stopSong(self):
    if self.songsQueue:
      self.clearQueue()
    if self.loop:
      self.loop = False
    if self.personalPlayList != None:
      self.personalPlayList = None
    self.client.stop()
    self.start_timestamp = None
    self.elapsed_time = 0
    self.currentSong = None
    await self.sendMessage("A mimir Zzz :sleeping:")

  async def skipSong(self):
    if self.getCurrentSong() != None:
      if self.songsQueue.qsize() != 0:
        if self.loop:
          self.currentSong = await self.songsQueue.get() 
        await self.sendMessage("Cambiando a la siguiente canción :track_next:")
        self.elapsed_time = 0
        self.client.stop()                             
      else:
        await self.sendMessage("**No hay más canciones en espera en el queue**")
        self.client.stop()

  async def loopSong(self):
    if self.getCurrentSong() != None:
      if self.loop:
        self.loop = False
        await self.sendMessage("Se detuvo el loop, volviendo a las canciones del queue mi ciela :nail_care:")    
      else:
        self.loop = True
        await self.sendMessage("**Reproduciendo en loop **"+self.getCurrentSong().getTitle())
    
  def clearVars(self):
    self.clearQueue()
    self.next.clear()
    self.currentSong = None
    self.lastSong = None
    self.start_timestamp = None
    self.elapsed_time = 0
    self.loop = False
    self.ctx = None
    self.client = None
    self.channel = None
    self.currentTask = None
    self.personalPlayList = None

  # Funciones del Personal PersonalPlayList

  def addSongToPersonalPlayList(self, song, userId):
    personalPlayList = self.personalPlayList.loadPlayList(userId)
    if(personalPlayList == None):
      personalPlayList = []
    personalPlayList.append(song)
    self.personalPlayList.savePlayList(userId, personalPlayList)

  async def getPersonalPlayList(self, memberId):
    """if self.personalPlayList.currentMember != memberId and self.personalPlayList.currentMember != None:
      await self.sendMessage("Alguien ya esta reproduciendo su playlist, espera tu turno panita.")
      return False"""
    if self.personalPlayList.getMember(memberId) != None:
      self.personalPlayList.playList = self.personalPlayList.loadPlayList(memberId)
      if self.personalPlayList.playList == None:
        await self.sendMessage("Tu playlist está vacia.")
        return False
      if len(self.personalPlayList.playList) == 0:
        await self.sendMessage("Tu playlist está vacia.")
        return False
      self.personalPlayList.currentMember = memberId
    else:
      await self.sendMessage("El usuario no tiene una playlist registrada.")
      return False    
    return True

  def addPersonalPlayListToQueue(self):
    self.clearQueue()
    self.client.stop()
    self.next.clear()
    self.currentSong = None
    self.lastSong = None
    self.start_timestamp = None
    self.elapsed_time = 0
    self.loop = False
    for song in self.personalPlayList.playList:
      self.songsQueue.put_nowait(song)

  async def listPlayList(self, memberId):
    member = self.personalPlayList.getMember(memberId);
    if member != None:
      personalPlayList = self.personalPlayList.loadPlayList(memberId)
      if personalPlayList == None:
        await self.sendMessage("La playlist está vacia.")
        return
      if len(personalPlayList) == 0:
        await self.sendMessage("La playlist está vacia.")
        return
      mensaje = "**Playlist de "+member+":\n**"
      for song in personalPlayList:
        mensaje += "- "+song.getTitle()+"\n"

      await self.sendMessage(mensaje)
    else:
      await self.sendMessage("El usuario no tiene una playlist regristrada.")

  async def listPlayListUsers(self):
    try:
      if len(self.personalPlayList.membersList) == 0:
        await self.sendMessage("No hay usuarios registrados con una Playlist.")
        return

      mensaje = "**Lista de miembros con un Playlist:\n**"      
      for key,value in self.personalPlayList.membersList.items():
        mensaje += "- "+value+"\n"
      await self.sendMessage(mensaje)
    except:
      await self.sendMessage("Hubo un problema.")
