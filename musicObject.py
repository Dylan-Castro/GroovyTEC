class MusicObject:
  filenameUrl = None
  youtubeUrl = None
  title = None

  def __init__(self,filenameUrl,youtubeUrl,title):
    self.filenameUrl = filenameUrl
    self.youtubeUrl = youtubeUrl
    self.title = title

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
