class MusicObject:
  filenameUrl = None
  youtubeUrl = None
  title = None
  thumbnail = None

  def __init__(self,filenameUrl,youtubeUrl,title,duration,thumbnail):
    self.filenameUrl = filenameUrl
    self.youtubeUrl = youtubeUrl
    self.title = title
    self.duration = duration
    self.thumbnail = thumbnail

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
  def getDuration(self):
    return self.duration
  def getThumbnail(self):
    return self.thumbnail

