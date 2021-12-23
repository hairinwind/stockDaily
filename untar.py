import tarfile
import os
import shutil

from globalSettings import tarPath, tarArchivePath

def untar(fname): 
    if fname.endswith("tar.gz"):
        tar = tarfile.open(fname, "r:gz")
        tar.extractall(path=str(tarPath))
        tar.close()
    elif fname.endswith("tar"):
        tar = tarfile.open(fname, "r:")
        tar.extractall(path=str(tarPath))
        tar.close()

def archiveFile(file):
    shutil.move(file, tarArchivePath)

def untarQuotes():
    files = os.listdir(tarPath)
    for file in files:
        tar_file = os.path.join(tarPath, file)
        print(tar_file)
        untar(tar_file)
        archiveFile(tar_file)

if __name__ == "__main__":
    print(str(tarPath))
    untarQuotes()
    
