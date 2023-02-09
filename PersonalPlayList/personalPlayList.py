import pickle
from pathlib import Path
class PersonalPlayList:
  playList = []
  membersList = {}
  currentMember = None

  def __init__(self):
    if Path("PersonalPlayList/membersList.pkl").exists():
      with open('PersonalPlayList/membersList.pkl', 'rb') as f:
        self.membersList = pickle.load(f)

  def loadPlayList(self, userId):
    if not Path('PersonalPlayList/ListFiles/PersonalPlayList_'+str(userId)+'.pkl').exists():
      return None
    with open('PersonalPlayList/ListFiles/PersonalPlayList_'+str(userId)+'.pkl', 'rb') as f:
     return pickle.load(f)

  def savePlayList(self, userId, playList):      
    with open('PersonalPlayList/ListFiles/PersonalPlayList_'+str(userId)+'.pkl', 'wb') as f:
     pickle.dump(playList, f)

  def addMember(self, user):
    if not user.id in self.membersList:
      self.membersList[user.id] = user.name
      with open('PersonalPlayList/membersList.pkl', 'wb') as f:
        pickle.dump(self.membersList, f)
    else:
      if self.membersList[user.id] != user.name:
        self.membersList[user.id] = user.name

  def getMember(self, userId):
    return self.membersList.get(userId, None)
  
  def checkMember(self, userId):
    if userId == self.currentMember:
      return True
    return False