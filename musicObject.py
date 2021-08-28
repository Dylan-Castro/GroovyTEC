class MusicObject:
  filenameUrl = None
  youtubeUrl = None
  title = None
  channel = None
  client = None
  ctx = None

  def __init__(self,filenameUrl,youtubeUrl,title,ctx):
    self.filenameUrl = filenameUrl
    self.youtubeUrl = youtubeUrl
    self.title = title
    self.channel = ctx.author.voice.channel
    self.client = ctx.channel.guild.voice_client
    self.ctx = ctx

  def getFilenameUrl(self):
    return self.filenameUrl
  def setFilenameUrl(self,filenameUrl):
    self.filenameUrl = filenameUrl
  def getYoutubeUrl(self):
    return self.youtubeUrl
  def setYoutubeUrl(self,youtubeUrl):
    self.youtubeUrl = youtubeUrl
  def getTitle(self):
    return self.title
  def setTitle(self,title):
    self.title = title 
  def getChannel(self):
    return self.channel
  def setChannel(self,channel):
    self.channel = channel
  def getClient(self):
    return self.client
  def setClient(self,client):
    self.client = client 
  def getCtx(self):
    return self.ctx
  def setCtx(self,ctx):
    self.ctx = ctx 
