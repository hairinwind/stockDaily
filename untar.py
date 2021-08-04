import tarfile
import os

def untar(fname): 
    if fname.endswith("tar.gz"):
        tar = tarfile.open(fname, "r:gz")
        tar.extractall(path="/home/yao/Downloads/quotes_tar")
        tar.close()
    elif fname.endswith("tar"):
        tar = tarfile.open(fname, "r:")
        tar.extractall(path="/home/yao/Downloads/quotes_tar")
        tar.close()

if __name__ == "__main__":
    path = "/home/yao/Downloads/quotes_tar"
    files = os.listdir(path)
    for file in files:
        tar_file = os.path.join(path, file)
        print(tar_file)
        untar(tar_file)
