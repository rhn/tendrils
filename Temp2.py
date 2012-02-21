import os

def ListAllFiles(Folder):
    for FileName in os.listdir(Folder):
        FilePath = os.path.join(Folder, FileName)
        if os.path.isfile(FilePath):
            print FilePath
        else:
            ListAllFiles(FilePath)

RootFolder = r"C:\Tendrils\Music\BGM"
ListAllFiles(RootFolder)